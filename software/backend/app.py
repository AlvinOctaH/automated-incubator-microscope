"""
Automated Incubator Microscope — Flask Backend (Raspberry Pi 4)
Fixes: camera init separate from Arduino connect, MJPEG live stream,
       capture works independently, scan handshake fixed, autofocus at A1 only.
"""

import io
import os
import json
import time
import threading
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import serial
import serial.tools.list_ports
import cv2
import numpy as np
from flask import Flask, jsonify, request, send_from_directory, Response
from picamera2 import Picamera2

# ─────────────────────────────────────────────
# App & Config
# ─────────────────────────────────────────────
BASE_DIR    = Path(__file__).parent.parent   # software/
FRONTEND    = BASE_DIR / "frontend"
CONFIG_PATH = BASE_DIR / "config.json"

DEFAULT_CONFIG = {
    "storage_path":           "/home/pi/microscope_data",
    "capture_interval_hours": 2,
    "settle_delay_ms":        500,
    "autofocus_z_range":      40,
    "autofocus_step_size":    5,
    "experiment_id":          "",
    "end_time":               "",
    "plate_type":             96,
    "folder_structure":       "DAY/BATCH",
    "serial_port":            "/dev/ttyUSB0",
    "baud_rate":              115200,
}

app = Flask(__name__, static_folder=str(FRONTEND), static_url_path="")

# ─────────────────────────────────────────────
# Global state
# ─────────────────────────────────────────────
state = {
    "arduino":            None,
    "camera":             None,
    "experiment_running": False,
    "experiment_thread":  None,
    "current_well":       "",
    "current_round":      0,
    "total_images":       0,
    "next_scan_at":       None,
    "experiment_end":     None,
    "experiment_id":      "",
    "storage_path":       DEFAULT_CONFIG["storage_path"],
    "plate_type":         96,
    "ejected":            False,
    "busy":               False,
    "last_sharpness":     0.0,
    "log":                [],
}

_serial_lock  = threading.Lock()
_frame_lock   = threading.Lock()
_latest_frame = None   # MJPEG frame bytes (JPEG)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def log(msg: str):
    ts    = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {msg}"
    state["log"].append(entry)
    if len(state["log"]) > 500:
        state["log"] = state["log"][-500:]
    print(entry)

def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            cfg = json.load(f)
        for k, v in DEFAULT_CONFIG.items():
            cfg.setdefault(k, v)
        return cfg
    return dict(DEFAULT_CONFIG)

def save_config(cfg: dict):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)

# ─────────────────────────────────────────────
# Camera
# ─────────────────────────────────────────────
def init_camera():
    """Initialise Picamera2 with preview config for live feed + still capture."""
    global _latest_frame
    cam = Picamera2()

    # Use video config for live feed (faster), switch to still for capture
    preview_cfg = cam.create_video_configuration(
        main={"size": (1280, 960), "format": "BGR888"},
    )
    cam.configure(preview_cfg)
    cam.start()
    time.sleep(1.5)
    state["camera"] = cam
    log("Camera initialised")

    # Start background thread to update live frame
    t = threading.Thread(target=_camera_loop, daemon=True)
    t.start()

def _camera_loop():
    """Continuously grab frames and encode as JPEG for MJPEG stream."""
    global _latest_frame
    cam = state["camera"]
    while cam is not None:
        try:
            arr = cam.capture_array()
            # Resize to 640x480 for stream (lighter)
            small = cv2.resize(arr, (640, 480))
            ok, buf = cv2.imencode(".jpg", small, [cv2.IMWRITE_JPEG_QUALITY, 80])
            if ok:
                with _frame_lock:
                    _latest_frame = buf.tobytes()
        except Exception:
            pass
        time.sleep(0.05)   # ~20 fps

def tenengrad(arr_bgr) -> float:
    gray = cv2.cvtColor(arr_bgr, cv2.COLOR_BGR2GRAY)
    gx   = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy   = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    return float(np.mean(gx**2 + gy**2))

def capture_image(save_path: Path, well: str, round_num: int) -> dict:
    cam = state["camera"]
    if cam is None:
        raise RuntimeError("Camera not initialised")
    save_path.mkdir(parents=True, exist_ok=True)
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{ts}_{well}_r{round_num:03d}"

    # Capture full-res still
    arr  = cam.capture_array()
    raw  = save_path / f"{stem}_raw.png"
    gray_arr = cv2.cvtColor(arr, cv2.COLOR_BGR2GRAY)
    gray = save_path / f"{stem}_gray.png"
    cv2.imwrite(str(raw),  arr)
    cv2.imwrite(str(gray), gray_arr)

    score = tenengrad(arr)
    state["total_images"]   += 2
    state["last_sharpness"]  = round(score, 2)
    return {"sharpness": round(score, 2), "raw": str(raw), "gray": str(gray)}

# ─────────────────────────────────────────────
# Serial
# ─────────────────────────────────────────────
def serial_send(cmd: str, wait_for: str = None, timeout: float = 30.0) -> str:
    ser = state["arduino"]
    if not ser or not ser.is_open:
        raise RuntimeError("Arduino not connected")
    with _serial_lock:
        ser.reset_input_buffer()
        ser.write((cmd + "\n").encode())
        if wait_for is None:
            return ""
        deadline = time.time() + timeout
        buf = []
        while time.time() < deadline:
            if ser.in_waiting:
                line = ser.readline().decode(errors="replace").strip()
                log(f"[ARD] {line}")
                buf.append(line)
                if wait_for in line:
                    return "\n".join(buf)
            else:
                time.sleep(0.005)
        raise TimeoutError(f"Timeout waiting for '{wait_for}'")

def serial_readline(timeout: float = 30.0) -> str:
    ser = state["arduino"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        if ser.in_waiting:
            return ser.readline().decode(errors="replace").strip()
        time.sleep(0.01)
    raise TimeoutError("Serial readline timeout")

# ─────────────────────────────────────────────
# Autofocus (Tenengrad sweep at A1 only)
# HIGH = naik = mendekati sample
# Sweep: turun half, naik step by step, kembali ke posisi terbaik
# ─────────────────────────────────────────────
def autofocus_at_a1(z_range: int, z_step: int, settle_s: float):
    log(f"Autofocus at A1: range={z_range} step={z_step}")
    cam  = state["camera"]
    half = z_range // 2

    # Turun ke batas bawah sweep
    serial_send(f"D {half}", wait_for="Z=")
    time.sleep(settle_s)

    scores    = []
    positions = list(range(0, z_range + z_step, z_step))

    for i, pos in enumerate(positions):
        arr   = cam.capture_array()
        score = tenengrad(arr)
        scores.append(score)

        if i < len(positions) - 1:
            serial_send(f"U {z_step}", wait_for="Z=")
            time.sleep(settle_s)

    best_idx = int(np.argmax(scores))
    best_pos = positions[best_idx]

    # Kembali ke posisi terbaik (turun dari posisi atas)
    steps_down = positions[-1] - best_pos
    if steps_down > 0:
        serial_send(f"D {steps_down}", wait_for="Z=")
        time.sleep(settle_s)

    log(f"Autofocus done. Best score={scores[best_idx]:.2f} at +{best_pos} from sweep start")

# ─────────────────────────────────────────────
# Folder helpers
# ─────────────────────────────────────────────
def get_batch_path(exp_root: Path, round_num: int, cfg: dict) -> Path:
    structure  = cfg.get("folder_structure", "DAY/BATCH")
    interval_h = float(cfg.get("capture_interval_hours", 2))
    if structure == "DAY/BATCH":
        total_h      = (round_num - 1) * interval_h
        day_num      = int(total_h // 24) + 1
        batch_in_day = round_num - int((day_num - 1) * 24 / interval_h)
        path = exp_root / f"DAY{day_num}" / f"Batch{batch_in_day:03d}"
    elif structure == "HOUR":
        total_h = int((round_num - 1) * interval_h)
        path    = exp_root / f"Hour_{total_h:04d}"
    else:
        path = exp_root / f"Round{round_num:03d}"
    path.mkdir(parents=True, exist_ok=True)
    return path

# ─────────────────────────────────────────────
# Experiment loop
# ─────────────────────────────────────────────
def experiment_loop(cfg: dict):
    state["experiment_running"] = True
    state["current_round"]      = 0
    state["total_images"]       = 0
    state["busy"]               = True

    try:
        base   = Path(cfg["storage_path"])
        exp_id = cfg.get("experiment_id") or f"EXP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        exp_root = base / exp_id
        exp_root.mkdir(parents=True, exist_ok=True)

        # Write metadata
        with open(exp_root / "metadata.json", "w") as f:
            json.dump({**cfg, "start_time": datetime.now().isoformat()}, f, indent=2)

        end_time   = datetime.fromisoformat(cfg["end_time"]) if cfg.get("end_time") else None
        interval_s = float(cfg["capture_interval_hours"]) * 3600
        settle_s   = float(cfg["settle_delay_ms"]) / 1000
        z_range    = int(cfg.get("autofocus_z_range", 40))
        z_step     = int(cfg.get("autofocus_step_size", 5))
        plate_type = int(cfg.get("plate_type", 96))

        serial_send(f"plate {plate_type}", wait_for="PLATE")
        state["experiment_end"] = end_time.isoformat() if end_time else None

        while state["experiment_running"]:
            if end_time and datetime.now() >= end_time:
                log("Experiment end time reached.")
                break

            state["current_round"] += 1
            rnd        = state["current_round"]
            batch_path = get_batch_path(exp_root, rnd, cfg)
            log(f"=== Round {rnd} ===")

            # Home → A1 → autofocus once
            serial_send("home", wait_for="HOMED", timeout=60)
            time.sleep(settle_s)
            autofocus_at_a1(z_range, z_step, settle_s)

            # Serpentine scan
            ser = state["arduino"]
            ser.reset_input_buffer()
            ser.write(b"scan\n")

            while state["experiment_running"]:
                line = serial_readline(timeout=30)
                log(f"[ARD] {line}")

                if line.startswith("AT "):
                    well = line[3:].strip()
                    state["current_well"] = well
                    well_path = batch_path / well
                    time.sleep(settle_s)
                    result = capture_image(well_path, well, rnd)
                    log(f"  {well} sharpness={result['sharpness']}")
                    ser.write(b"OK\n")

                elif line == "SCAN_DONE":
                    log(f"Round {rnd} done. Total images: {state['total_images']}")
                    break
                elif line in ("STOP", "TIMEOUT"):
                    log(f"Scan aborted: {line}")
                    state["experiment_running"] = False
                    break

            # Wait for next interval
            if state["experiment_running"]:
                next_scan = datetime.now() + timedelta(seconds=interval_s)
                state["next_scan_at"] = next_scan.isoformat()
                log(f"Next scan at {next_scan.strftime('%H:%M:%S')}")
                while datetime.now() < next_scan and state["experiment_running"]:
                    time.sleep(1)

    except Exception as e:
        log(f"ERROR: {e}")
    finally:
        state["experiment_running"] = False
        state["busy"]               = False
        state["next_scan_at"]       = None
        log("Experiment ended.")

# ─────────────────────────────────────────────
# USB detection
# ─────────────────────────────────────────────
def list_usb_drives():
    drives = []
    try:
        r    = subprocess.run(["lsblk", "-J", "-o", "NAME,MOUNTPOINT,SIZE,TYPE,TRAN"],
                               capture_output=True, text=True)
        data = json.loads(r.stdout)
        for dev in data.get("blockdevices", []):
            if dev.get("tran") == "usb":
                for child in dev.get("children", [dev]):
                    mp = child.get("mountpoint")
                    if mp and mp != "[SWAP]":
                        drives.append({"name": f"{child['name']} ({child.get('size','?')})",
                                       "path": mp, "size": child.get("size", "?")})
    except Exception as e:
        log(f"USB detect error: {e}")
    drives.append({"name": "Local storage", "path": "/home/pi/microscope_data", "size": ""})
    return drives

# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory(str(FRONTEND), "index.html")

@app.route("/api/status")
def api_status():
    return jsonify({
        "connected":          state["arduino"] is not None and state["arduino"].is_open,
        "camera_ready":       state["camera"] is not None,
        "experiment_running": state["experiment_running"],
        "current_well":       state["current_well"],
        "current_round":      state["current_round"],
        "total_images":       state["total_images"],
        "next_scan_at":       state["next_scan_at"],
        "experiment_end":     state["experiment_end"],
        "plate_type":         state["plate_type"],
        "busy":               state["busy"],
        "ejected":            state["ejected"],
        "last_sharpness":     state["last_sharpness"],
        "log":                state["log"][-60:],
    })

# --- MJPEG live stream ---
@app.route("/api/stream")
def api_stream():
    def generate():
        while True:
            with _frame_lock:
                frame = _latest_frame
            if frame:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")
            time.sleep(0.05)
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")

# --- Connect Arduino (separate from camera) ---
@app.route("/api/connect", methods=["POST"])
def api_connect():
    data = request.json or {}
    port = data.get("port", "/dev/ttyUSB0")
    baud = int(data.get("baud", 115200))
    try:
        if state["arduino"] and state["arduino"].is_open:
            state["arduino"].close()
        ser = serial.Serial(port, baud, timeout=2)
        time.sleep(2)
        state["arduino"] = ser
        log(f"Arduino connected on {port}")
        return jsonify({"ok": True, "port": port})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Init camera separately ---
@app.route("/api/camera/init", methods=["POST"])
def api_camera_init():
    try:
        if state["camera"] is None:
            init_camera()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Ports ---
@app.route("/api/ports")
def api_ports():
    ports = [p.device for p in serial.tools.list_ports.comports()]
    return jsonify(ports)

# --- Drives ---
@app.route("/api/drives")
def api_drives():
    return jsonify(list_usb_drives())

# --- Generic command ---
@app.route("/api/cmd", methods=["POST"])
def api_cmd():
    cmd = (request.json or {}).get("cmd", "")
    try:
        # For Z moves we want the Z= response
        wait = "Z=" if cmd.upper().startswith(("U", "D")) else None
        resp = serial_send(cmd, wait_for=wait, timeout=15)
        return jsonify({"ok": True, "response": resp})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Move to well ---
@app.route("/api/move/<well>", methods=["POST"])
def api_move(well):
    try:
        resp = serial_send(well.upper(), wait_for="MOVED", timeout=20)
        state["current_well"] = well.upper()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Home ---
@app.route("/api/home", methods=["POST"])
def api_home():
    try:
        state["busy"] = True
        serial_send("home", wait_for="HOMED", timeout=60)
        state["busy"] = False
        return jsonify({"ok": True})
    except Exception as e:
        state["busy"] = False
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Stop ---
@app.route("/api/stop", methods=["POST"])
def api_stop():
    state["experiment_running"] = False
    state["busy"]               = False
    try:
        state["arduino"].write(b"stop\n")
    except:
        pass
    return jsonify({"ok": True})

# --- Plate type ---
@app.route("/api/plate/<int:ptype>", methods=["POST"])
def api_plate(ptype):
    if ptype not in (96, 36):
        return jsonify({"ok": False, "error": "Use 96 or 36"}), 400
    state["plate_type"] = ptype
    try:
        serial_send(f"plate {ptype}", wait_for="PLATE", timeout=5)
    except:
        pass
    return jsonify({"ok": True, "plate": ptype})

# --- Capture ---
@app.route("/api/capture", methods=["POST"])
def api_capture():
    try:
        if state["camera"] is None:
            return jsonify({"ok": False, "error": "Camera not initialised"}), 400
        path   = Path(state["storage_path"]) / "manual"
        result = capture_image(path, state["current_well"] or "manual", 0)
        return jsonify({"ok": True, **result})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Eject ---
@app.route("/api/eject", methods=["POST"])
def api_eject():
    try:
        serial_send("eject", wait_for="EJECTED", timeout=60)
        state["ejected"] = True
        log("Stage ejected")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Return ---
@app.route("/api/return", methods=["POST"])
def api_return():
    try:
        serial_send("return", wait_for="HOMED", timeout=60)
        state["ejected"]      = False
        state["current_well"] = ""
        log("Stage returned to home")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Start experiment ---
@app.route("/api/experiment/start", methods=["POST"])
def api_experiment_start():
    if state["experiment_running"]:
        return jsonify({"ok": False, "error": "Already running"}), 409
    if state["camera"] is None:
        return jsonify({"ok": False, "error": "Camera not initialised"}), 400
    cfg = request.json or {}
    save_config(cfg)
    state["experiment_id"]  = cfg.get("experiment_id", "")
    state["storage_path"]   = cfg.get("storage_path", DEFAULT_CONFIG["storage_path"])
    state["plate_type"]     = int(cfg.get("plate_type", 96))
    t = threading.Thread(target=experiment_loop, args=(cfg,), daemon=True)
    t.start()
    state["experiment_thread"] = t
    return jsonify({"ok": True})

# --- Stop experiment ---
@app.route("/api/experiment/stop", methods=["POST"])
def api_experiment_stop():
    state["experiment_running"] = False
    try:
        state["arduino"].write(b"stop\n")
    except:
        pass
    return jsonify({"ok": True})

# --- Config ---
@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "GET":
        return jsonify(load_config())
    save_config(request.json or {})
    return jsonify({"ok": True})

# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Auto-init camera on startup
    try:
        init_camera()
    except Exception as e:
        print(f"Camera init failed on startup: {e}")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
