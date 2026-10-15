"""
Y AXIS REPEATABILITY VALIDATION
==================================
Mengukur seberapa repeatable sumbu Y kembali ke posisi yang sama.
Target well default: E1 (pure Y motion, X=0)

Mode:
  nohome (default) — balik ke A1 antar repetisi, mirip kondisi scan nyata
  home             — home tiap repetisi
  both             — jalankan keduanya untuk perbandingan

Cara pakai:
  python3 y_repeatability.py --port /dev/ttyACM0 --reps 10
  python3 y_repeatability.py --port /dev/ttyACM0 --reps 10 --mode home
  python3 y_repeatability.py --port /dev/ttyACM0 --reps 10 --mode both

Output:
  repeatability_output/
    y_axis/            ← foto repetisi Y
    overlay_y.png      ← semua foto Y di-superimpose
    displacement_y.csv ← dx, dy, dist per rep Y
    plot_y.png         ← grafik displacement Y
    summary.txt        ← stats lengkap + interpretasi
"""

import os
import csv
import time
import argparse
import serial
import cv2
import numpy as np
from picamera2 import Picamera2

# ─────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────
OUT_DIR    = "repeatability_output"
RESET_WELL = "A1"   # titik balik antar repetisi pada mode nohome

# ─────────────────────────────────────────────
# Serial helpers
# ─────────────────────────────────────────────
def serial_send(ser, cmd):
    ser.write((cmd + "\n").encode())

def wait_for(ser, keyword, timeout=60.0):
    deadline = time.time() + timeout
    buf = []
    while time.time() < deadline:
        if ser.in_waiting:
            line = ser.readline().decode(errors="replace").strip()
            print(f"  [ARD] {line}")
            buf.append(line)
            if keyword in line:
                return "\n".join(buf)
        time.sleep(0.01)
    raise TimeoutError(f"Timeout waiting for '{keyword}'")

# ─────────────────────────────────────────────
# Camera
# ─────────────────────────────────────────────
def init_camera():
    cam = Picamera2()
    cam.configure(cam.create_still_configuration(
        main={"size": (4056, 3040), "format": "BGR888"}
    ))
    cam.start()
    time.sleep(2)
    return cam

def capture(cam, settle_s=0.5):
    time.sleep(settle_s)
    return cam.capture_array()

# ─────────────────────────────────────────────
# Phase correlation — ukur displacement antar dua gambar
# Returns (dx, dy) dalam pixel
# ─────────────────────────────────────────────
def measure_displacement(ref_img, cur_img):
    ref_g = cv2.cvtColor(ref_img, cv2.COLOR_BGR2GRAY).astype(np.float32)
    cur_g = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY).astype(np.float32)

    # Crop center 512x512 — fokus ke area well
    h, w  = ref_g.shape
    cy, cx = h//2, w//2
    s     = 512
    ref_crop = ref_g[cy-s:cy+s, cx-s:cx+s]
    cur_crop = cur_g[cy-s:cy+s, cx-s:cx+s]

    shift, _ = cv2.phaseCorrelate(ref_crop, cur_crop)
    dx, dy   = shift
    return round(dx, 3), round(dy, 3)

# ─────────────────────────────────────────────
# Overlay — superimpose semua gambar
# Kalau repeatable → hasil tajam
# Kalau tidak repeatable → blur / ghosting
# ─────────────────────────────────────────────
def make_overlay(images, out_path):
    if not images:
        return
    resized = [cv2.resize(img, (640, 480)) for img in images]
    overlay = np.zeros_like(resized[0], dtype=np.float64)
    for img in resized:
        overlay += img.astype(np.float64)
    overlay /= len(resized)
    cv2.imwrite(out_path, overlay.astype(np.uint8))
    print(f"Overlay saved: {out_path}")

# ─────────────────────────────────────────────
# Plot displacement
# ─────────────────────────────────────────────
def plot_displacement(displacements, axis_name, mode_label, out_path):
    n    = len(displacements)
    W, H = max(600, n*40+100), 320
    img  = np.ones((H, W, 3), dtype=np.uint8) * 245
    FONT = cv2.FONT_HERSHEY_SIMPLEX

    if n < 2:
        cv2.imwrite(out_path, img)
        return

    dxs      = [d[0] for d in displacements]
    dys      = [d[1] for d in displacements]
    dists    = [(d[0]**2+d[1]**2)**0.5 for d in displacements]
    all_vals = dxs + dys
    vmax     = max(abs(min(all_vals)), abs(max(all_vals)), 1.0)

    mid    = H // 2
    pad    = 55
    w_per  = (W - pad*2) / max(n-1, 1)

    # Zero line
    cv2.line(img, (pad, mid), (W-pad, mid), (180,180,180), 1)

    # Y axis labels
    cv2.putText(img, f"+{vmax:.1f}px", (4, pad+10), FONT, 0.3, (130,130,130), 1)
    cv2.putText(img, f"-{vmax:.1f}px", (4, H-pad+5), FONT, 0.3, (130,130,130), 1)
    cv2.putText(img, "0", (4, mid+4), FONT, 0.3, (130,130,130), 1)

    def val_to_y(v):
        return int(mid - (v / vmax) * (H//2 - 35))

    # dx line — biru
    for i in range(n-1):
        x1 = int(pad + i*w_per)
        x2 = int(pad + (i+1)*w_per)
        cv2.line(img, (x1, val_to_y(dxs[i])), (x2, val_to_y(dxs[i+1])), (200,80,50), 2)
    for i in range(n):
        cv2.circle(img, (int(pad+i*w_per), val_to_y(dxs[i])), 4, (200,80,50), -1)

    # dy line — hijau
    for i in range(n-1):
        x1 = int(pad + i*w_per)
        x2 = int(pad + (i+1)*w_per)
        cv2.line(img, (x1, val_to_y(dys[i])), (x2, val_to_y(dys[i+1])), (50,160,80), 2)
    for i in range(n):
        cv2.circle(img, (int(pad+i*w_per), val_to_y(dys[i])), 4, (50,160,80), -1)

    # dist line — abu
    for i in range(n-1):
        x1 = int(pad + i*w_per)
        x2 = int(pad + (i+1)*w_per)
        cv2.line(img, (x1, val_to_y(dists[i])), (x2, val_to_y(dists[i+1])), (120,120,200), 1)

    # Rep numbers di bawah
    for i in range(n):
        x = int(pad + i*w_per)
        cv2.putText(img, str(i+1), (x-4, H-8), FONT, 0.3, (100,100,100), 1)

    # Legend
    cv2.rectangle(img, (W-145, 15), (W-131, 25), (200,80,50), -1)
    cv2.putText(img, "dx", (W-127, 24), FONT, 0.35, (50,50,50), 1)
    cv2.rectangle(img, (W-145, 32), (W-131, 42), (50,160,80), -1)
    cv2.putText(img, "dy", (W-127, 41), FONT, 0.35, (50,50,50), 1)
    cv2.rectangle(img, (W-145, 49), (W-131, 59), (120,120,200), -1)
    cv2.putText(img, "dist", (W-127, 58), FONT, 0.35, (50,50,50), 1)

    title = f"{axis_name} Axis Repeatability [{mode_label}] — Displacement per Rep"
    cv2.putText(img, title, (pad, 18), FONT, 0.4, (30,30,30), 1)
    cv2.putText(img, "Rep #", (pad, H-8), FONT, 0.3, (130,130,130), 1)

    cv2.imwrite(out_path, img)
    print(f"Plot saved: {out_path}")

# ─────────────────────────────────────────────
# Run one axis repeatability test
# mode: "nohome" → balik ke A1 antar rep
#       "home"   → home tiap rep
# ─────────────────────────────────────────────
def run_axis_test(ser, cam, axis_name, well_target, reps, settle_s, out_subdir, mode="nohome"):
    os.makedirs(out_subdir, exist_ok=True)

    reset_label = RESET_WELL if mode == "nohome" else "HOME"
    print(f"\n{'═'*55}")
    print(f"  {axis_name} Axis Repeatability — mode: {mode.upper()}")
    print(f"  Target well : {well_target}")
    print(f"  Reset to    : {reset_label}")
    print(f"  Repetitions : {reps}")
    print(f"{'═'*55}")

    images        = []
    displacements = []
    ref_img       = None

    # Home sekali di awal
    print("\nHoming to start position...")
    serial_send(ser, "home")
    wait_for(ser, "HOMED", timeout=60)

    for rep in range(1, reps+1):
        print(f"\n--- Rep {rep}/{reps} ---")

        # Reset position antar rep
        if rep > 1:
            if mode == "home":
                serial_send(ser, "home")
                wait_for(ser, "HOMED", timeout=60)
            else:
                # Balik ke A1 dulu
                serial_send(ser, RESET_WELL)
                wait_for(ser, "MOVED", timeout=20)

        # Gerak ke well target
        serial_send(ser, well_target)
        wait_for(ser, "MOVED", timeout=20)

        # Capture
        arr   = capture(cam, settle_s)
        fname = os.path.join(out_subdir, f"rep_{rep:03d}.png")
        cv2.imwrite(fname, arr)
        images.append(arr)
        print(f"  Saved: {fname}")

        if rep == 1:
            ref_img = arr
            displacements.append((0.0, 0.0))
            print(f"  → Reference image set")
        else:
            dx, dy = measure_displacement(ref_img, arr)
            dist   = round((dx**2 + dy**2)**0.5, 3)
            displacements.append((dx, dy))
            print(f"  → dx={dx:+.3f}px  dy={dy:+.3f}px  dist={dist:.3f}px")

    return images, displacements

# ─────────────────────────────────────────────
# Stats
# ─────────────────────────────────────────────
def calc_stats(displacements, pixel_size_um=None):
    data  = displacements[1:]   # skip rep 1 (referensi, selalu 0)
    if not data:
        return {}
    dxs   = [d[0] for d in data]
    dys   = [d[1] for d in data]
    dists = [(d[0]**2+d[1]**2)**0.5 for d in data]
    stats = {
        "mean_dx_px":   round(float(np.mean(dxs)),   3),
        "std_dx_px":    round(float(np.std(dxs)),    3),
        "mean_dy_px":   round(float(np.mean(dys)),   3),
        "std_dy_px":    round(float(np.std(dys)),    3),
        "mean_dist_px": round(float(np.mean(dists)), 3),
        "std_dist_px":  round(float(np.std(dists)),  3),
        "max_dist_px":  round(float(np.max(dists)),  3),
    }
    if pixel_size_um:
        stats["mean_dist_um"] = round(np.mean(dists) * pixel_size_um, 2)
        stats["max_dist_um"]  = round(np.max(dists)  * pixel_size_um, 2)
        stats["std_dist_um"]  = round(np.std(dists)  * pixel_size_um, 2)
    return stats

def save_csv(displacements, out_path):
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rep", "dx_px", "dy_px", "dist_px"])
        for i, (dx, dy) in enumerate(displacements):
            dist = round((dx**2+dy**2)**0.5, 3)
            writer.writerow([i+1, dx, dy, dist])
    print(f"CSV saved: {out_path}")

def format_stat_block(label, stats, pixel_size_um):
    lines = [
        f"─── {label} ───────────────────────────────────",
        f"  Mean displacement : {stats.get('mean_dist_px','?')} px",
        f"  Std deviation     : {stats.get('std_dist_px','?')} px",
        f"  Max displacement  : {stats.get('max_dist_px','?')} px",
        f"  Mean dx           : {stats.get('mean_dx_px','?')} px",
        f"  Mean dy           : {stats.get('mean_dy_px','?')} px",
    ]
    if pixel_size_um and "mean_dist_um" in stats:
        lines += [
        f"  Mean (µm)         : {stats['mean_dist_um']} µm",
        f"  Std  (µm)         : {stats['std_dist_um']} µm",
        f"  Max  (µm)         : {stats['max_dist_um']} µm",
        ]
    return lines

def save_summary(results, well_x, well_y, reps, mode, pixel_size_um, out_path):
    lines = [
        "═══════════════════════════════════════════════",
        "  Y AXIS REPEATABILITY — SUMMARY",
        "═══════════════════════════════════════════════",
        f"  Repetitions : {reps}",
        f"  Y test well : {well_y}  (pure Y motion, X=0)",
        f"  Mode        : {mode}",
        f"  Reset to    : {RESET_WELL if mode != 'home' else 'HOME'} between reps",
        f"  Pixel size  : {pixel_size_um} µm/px" if pixel_size_um else
        f"  Pixel size  : not set (results in px only)",
        "",
    ]

    for label, stats in results:
        lines += format_stat_block(label, stats, pixel_size_um)
        lines.append("")

    lines += [
        "─── INTERPRETATION ────────────────────────────",
        "  < 1 px  (< ~2 µm)  : Excellent repeatability",
        "  1–3 px  (~2–5 µm)  : Good, acceptable for imaging",
        "  3–10 px (~5–15 µm) : Moderate — check mechanical play",
        "  > 10 px (> 15 µm)  : Poor — needs mechanical fix",
        "═══════════════════════════════════════════════",
    ]

    text = "\n".join(lines)
    with open(out_path, "w") as f:
        f.write(text)
    print("\n" + text)
    print(f"\nSummary saved: {out_path}")

# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
def main(port, baud, reps, well_y, settle_ms, pixel_size_um, mode):
    os.makedirs(OUT_DIR, exist_ok=True)
    settle_s = settle_ms / 1000.0

    print("Initialising camera...")
    cam = init_camera()
    print("Camera ready.")

    print(f"Connecting Arduino on {port}...")
    ser = serial.Serial(port, baud, timeout=2)
    time.sleep(2)
    ser.reset_input_buffer()
    print("Arduino connected.")

    all_results = []   # list of (label, stats) untuk summary

    if mode == "both":
        modes_to_run = ["nohome", "home"]
    else:
        modes_to_run = [mode]

    for m in modes_to_run:
        suffix = f"_{m}" if mode == "both" else ""

        # ── Y axis only ──
        input(f"\nPress Enter to start Y axis test [{m}] (well: {well_y}, {reps} reps)...")
        imgs_y, disp_y = run_axis_test(
            ser, cam, "Y", well_y, reps, settle_s,
            os.path.join(OUT_DIR, f"y_axis{suffix}"), mode=m
        )
        make_overlay(imgs_y, os.path.join(OUT_DIR, f"overlay_y{suffix}.png"))
        save_csv(disp_y,    os.path.join(OUT_DIR, f"displacement_y{suffix}.csv"))
        plot_displacement(disp_y, "Y", m, os.path.join(OUT_DIR, f"plot_y{suffix}.png"))
        stats_y = calc_stats(disp_y, pixel_size_um)
        all_results.append((f"Y Axis [{m}] — well {well_y}", stats_y))

    save_summary(all_results, None, well_y, reps, mode, pixel_size_um,
                 os.path.join(OUT_DIR, "summary.txt"))

    cam.stop()
    ser.close()
    print("\nAll done!")

# ─────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Y Axis Repeatability Validation")
    parser.add_argument("--port",          default="/dev/ttyACM0")
    parser.add_argument("--baud",          type=int,   default=115200)
    parser.add_argument("--reps",          type=int,   default=10,
                        help="Jumlah repetisi (default: 10)")
    parser.add_argument("--well-y",        default="E1",
                        help="Well untuk test Y axis — pure Y motion (default: E1)")
    parser.add_argument("--settle-ms",     type=int,   default=500,
                        help="Settle delay setelah motor berhenti, ms (default: 500)")
    parser.add_argument("--pixel-size-um", type=float, default=None,
                        help="Ukuran pixel dalam µm untuk konversi px→µm (opsional)")
    parser.add_argument("--mode",          default="nohome",
                        choices=["nohome", "home", "both"],
                        help="nohome=balik ke A1 antar rep (default), home=home tiap rep, both=keduanya")
    args = parser.parse_args()

    main(args.port, args.baud, args.reps,
         args.well_y.upper(),
         args.settle_ms, args.pixel_size_um, args.mode)
