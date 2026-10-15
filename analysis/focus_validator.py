#!/usr/bin/env python3
"""
Z Focus Repeatability Validator — Raspberry Pi
===============================================
Validasi dua hal sekaligus:
  1. SHARPNESS   — apakah fokus sama setiap siklus (Laplacian Variance)
  2. POSISI SHIFT — apakah posisi XY bergeser (Phase Correlation)

Install:
  pip install pyserial opencv-python numpy

Jalankan:
  python3 focus_validator.py

Perintah:
  setzero              — set posisi Z sekarang sebagai baseline
  U                    — Z naik manual
  D                    — Z turun manual
  status               — cek posisi Z
  home                 — homing XY
  validate <pulse> <n> — mulai validasi
  quit / exit          — keluar
"""

import serial
import serial.tools.list_ports
import subprocess
import threading
import time
import os
import csv
import numpy as np
import cv2
from datetime import datetime

# ============================
# KONFIGURASI
# ============================
BAUD_RATE     = 9600
IMAGE_DIR     = "./validation_images"
CAPTURE_DELAY = 0.8   # detik jeda sebelum ambil gambar

# ============================
# CARI PORT ARDUINO
# ============================
def find_arduino_port():
    for p in serial.tools.list_ports.comports():
        dev = p.device.lower()
        if "ttyacm" in dev or "ttyusb" in dev:
            print(f"[INFO] Arduino ditemukan: {p.device}")
            return p.device
    print("[WARN] Port tidak ditemukan otomatis, pakai /dev/ttyACM0")
    return "/dev/ttyACM0"

# ============================
# AMBIL GAMBAR
# ============================
def capture_image(filepath):
    cmd = [
        "rpicam-still",
        "--output", filepath,
        "--nopreview",
        "--timeout", "500",
        "--width",  "1920",
        "--height", "1080",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] rpicam-still gagal:\n{result.stderr}")
        return False
    return True

# ============================
# HITUNG SHARPNESS — Laplacian Variance
# Makin tinggi = makin fokus
# ============================
def compute_sharpness(filepath):
    img = cv2.imread(filepath)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    roi  = gray[h//4: h*3//4, w//4: w*3//4]
    return round(cv2.Laplacian(roi, cv2.CV_64F).var(), 4)

# ============================
# HITUNG SHIFT POSISI — Phase Correlation
# Bandingkan gambar siklus vs gambar baseline
# Return (shift_x, shift_y) dalam pixel
# ============================
def compute_shift(ref_img_gray, cur_filepath):
    cur = cv2.imread(cur_filepath)
    if cur is None:
        return None, None
    cur_gray = cv2.cvtColor(cur, cv2.COLOR_BGR2GRAY)

    # Crop ROI tengah supaya tidak terpengaruh tepi
    h, w = ref_img_gray.shape
    ref_roi = ref_img_gray[h//4: h*3//4, w//4: w*3//4].astype(np.float32)
    cur_roi = cur_gray   [h//4: h*3//4, w//4: w*3//4].astype(np.float32)

    # Phase correlation — return (shift_x, shift_y)
    (shift_x, shift_y), _ = cv2.phaseCorrelate(ref_roi, cur_roi)

    # Shift negatif artinya gambar bergeser ke arah sebaliknya
    return round(shift_x, 3), round(shift_y, 3)

# ============================
# CETAK STATISTIK
# ============================
def print_statistics(sharpness_vals, shift_x_vals, shift_y_vals):
    if not sharpness_vals:
        return

    def stats(arr, label, unit=""):
        a    = np.array(arr)
        mean = np.mean(a)
        std  = np.std(a)
        mn   = np.min(a)
        mx   = np.max(a)
        cv   = (std / mean * 100) if mean else 0
        print(f"\n  [{label}]")
        print(f"    Mean   : {mean:.4f} {unit}")
        print(f"    Std Dev: {std:.4f} {unit}")
        print(f"    Min    : {mn:.4f} {unit}")
        print(f"    Max    : {mx:.4f} {unit}")
        print(f"    Range  : {mx - mn:.4f} {unit}")
        if unit == "":  # hanya sharpness yang pakai CV
            print(f"    CV (%) : {cv:.2f}%")
            if   cv < 2:  print(f"    >> SANGAT BAIK  (CV < 2%)")
            elif cv < 5:  print(f"    >> BAIK         (CV 2-5%)")
            elif cv < 10: print(f"    >> CUKUP        (CV 5-10%) — cek backlash")
            else:         print(f"    >> BURUK        (CV > 10%) — ada masalah mekanik")
        return mean, std, mn, mx

    print("\n========================================")
    print("     HASIL VALIDASI REPEATABILITY")
    print("========================================")
    print(f"  Jumlah siklus: {len(sharpness_vals)}")

    stats(sharpness_vals, "SHARPNESS (fokus)")

    if shift_x_vals and shift_y_vals:
        sx = np.array(shift_x_vals)
        sy = np.array(shift_y_vals)
        # Magnitude total shift
        mag = np.sqrt(sx**2 + sy**2)
        stats(shift_x_vals, "SHIFT X (pixel)", "px")
        stats(shift_y_vals, "SHIFT Y (pixel)", "px")
        print(f"\n  [SHIFT TOTAL (magnitude)]")
        print(f"    Mean   : {np.mean(mag):.3f} px")
        print(f"    Max    : {np.max(mag):.3f} px")
        if np.max(mag) < 1.0:
            print(f"    >> POSISI SANGAT STABIL (< 1 px)")
        elif np.max(mag) < 3.0:
            print(f"    >> POSISI STABIL (< 3 px)")
        elif np.max(mag) < 7.0:
            print(f"    >> POSISI CUKUP (< 7 px) — ada sedikit geser")
        else:
            print(f"    >> POSISI TIDAK STABIL (> 7 px) — cek mekanik")

    print("\n========================================")
    print("Data mentah:")
    print(f"  {'Siklus':>6}  {'Sharpness':>12}  {'Shift X':>10}  {'Shift Y':>10}")
    print(f"  {'------':>6}  {'----------':>12}  {'--------':>10}  {'--------':>10}")
    for i in range(len(sharpness_vals)):
        sx = f"{shift_x_vals[i]:>10.3f}" if i < len(shift_x_vals) else f"{'N/A':>10}"
        sy = f"{shift_y_vals[i]:>10.3f}" if i < len(shift_y_vals) else f"{'N/A':>10}"
        print(f"  {i+1:>6}  {sharpness_vals[i]:>12.4f}  {sx}  {sy}")
    print("========================================")

# ============================
# SIMPAN CSV
# ============================
def save_csv(results, session_time):
    path = f"focus_results_{session_time}.csv"
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cycle", "timestamp", "sharpness", "shift_x_px", "shift_y_px", "shift_mag_px", "image_path"])
        for r in results:
            w.writerow(r)
    print(f"\n[INFO] CSV disimpan: {path}")

# ============================
# THREAD: baca serial dari Arduino
# ============================
arduino_lines = []
serial_lock   = threading.Lock()

def serial_reader(ser):
    while True:
        try:
            line = ser.readline().decode("utf-8", errors="ignore").strip()
            if line:
                with serial_lock:
                    arduino_lines.append(line)
        except:
            break

def wait_for_line(keyword, timeout=60):
    t0 = time.time()
    while time.time() - t0 < timeout:
        with serial_lock:
            for i, line in enumerate(arduino_lines):
                if keyword in line:
                    arduino_lines.pop(i)
                    return line
        time.sleep(0.05)
    return None

def flush_print():
    with serial_lock:
        for line in arduino_lines:
            print(f"[Arduino] {line}")
        arduino_lines.clear()

# ============================
# VALIDASI
# ============================
def run_validation(ser, pulse, reps):
    os.makedirs(IMAGE_DIR, exist_ok=True)
    session_time   = datetime.now().strftime("%Y%m%d_%H%M%S")
    results        = []
    sharpness_vals = []
    shift_x_vals   = []
    shift_y_vals   = []
    ref_gray       = None   # gambar baseline untuk perbandingan shift

    print(f"\n[INFO] Mulai validasi: {reps} siklus, {pulse} pulse per siklus")
    ser.write(f"validate {pulse} {reps}\n".encode())

    line = wait_for_line("START", timeout=10)
    if not line:
        print("[ERROR] Arduino tidak merespons.")
        return
    print(f"[Arduino] {line}")

    for cycle in range(1, reps + 1):
        line = wait_for_line("CYCLE", timeout=30)
        if line:
            print(f"[Arduino] {line}")

        line = wait_for_line("READY", timeout=90)
        if not line:
            print("[ERROR] Timeout menunggu READY.")
            break
        print(f"[Arduino] {line}")

        # Ambil gambar
        ts       = datetime.now().strftime("%H%M%S_%f")
        img_path = os.path.join(IMAGE_DIR, f"cycle_{cycle:03d}_{ts}.jpg")
        print(f"  [Raspi] Ambil gambar siklus {cycle}...")
        time.sleep(CAPTURE_DELAY)

        ok = capture_image(img_path)
        if not ok:
            ser.write(b"0\n")
            time.sleep(0.5)
            continue

        # Hitung sharpness
        sharpness = compute_sharpness(img_path)
        if sharpness is None:
            sharpness = 0.0
        print(f"  [Raspi] Sharpness  : {sharpness:.4f}")
        sharpness_vals.append(sharpness)

        # Hitung shift posisi
        cur_img = cv2.imread(img_path)
        if cur_img is not None:
            cur_gray = cv2.cvtColor(cur_img, cv2.COLOR_BGR2GRAY)
            if ref_gray is None:
                # Siklus pertama = jadikan referensi baseline
                ref_gray = cur_gray.copy()
                sx, sy   = 0.0, 0.0
                print(f"  [Raspi] Shift      : baseline (siklus 1 = referensi)")
            else:
                sx, sy = compute_shift(ref_gray, img_path)
                if sx is None:
                    sx, sy = 0.0, 0.0
                print(f"  [Raspi] Shift X/Y  : {sx:.3f} px / {sy:.3f} px  (mag: {(sx**2+sy**2)**0.5:.3f} px)")
            shift_x_vals.append(sx)
            shift_y_vals.append(sy)
            mag = round((sx**2 + sy**2) ** 0.5, 3)
        else:
            sx, sy, mag = 0.0, 0.0, 0.0

        results.append([cycle, ts, sharpness, sx, sy, mag, img_path])

        # Kirim sharpness ke Arduino
        ser.write(f"{sharpness:.4f}\n".encode())
        time.sleep(0.5)

        flush_print()

    wait_for_line("DONE", timeout=15)
    print("\n[INFO] Validasi selesai!")

    print_statistics(sharpness_vals, shift_x_vals, shift_y_vals)
    save_csv(results, session_time)

# ============================
# MAIN
# ============================
def main():
    port = find_arduino_port()
    print(f"[INFO] Konek ke {port} @ {BAUD_RATE}...")

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
    except serial.SerialException as e:
        print(f"[ERROR] Gagal buka serial: {e}")
        print("Cek port: ls /dev/ttyACM* /dev/ttyUSB*")
        return

    time.sleep(2)
    ser.reset_input_buffer()

    t = threading.Thread(target=serial_reader, args=(ser,), daemon=True)
    t.start()

    print("\n========================================")
    print("  Z Focus Validator — Terminal Mode")
    print("========================================")
    print("  setzero              → set Z baseline")
    print("  U                    → Z naik manual")
    print("  D                    → Z turun manual")
    print("  status               → cek posisi Z")
    print("  home                 → homing XY")
    print("  validate <pulse> <n> → mulai validasi")
    print("  quit                 → keluar")
    print("========================================\n")

    try:
        while True:
            flush_print()
            cmd = input(">> ").strip()
            if not cmd:
                continue

            if cmd.lower() in ("quit", "exit"):
                print("Keluar.")
                break

            elif cmd.lower().startswith("validate"):
                parts = cmd.split()
                if len(parts) != 3:
                    print("Format: validate <pulse> <n>   contoh: validate 500 10")
                    continue
                try:
                    pulse = int(parts[1])
                    reps  = int(parts[2])
                except ValueError:
                    print("Pulse dan n harus angka.")
                    continue
                run_validation(ser, pulse, reps)

            else:
                ser.write(f"{cmd}\n".encode())
                time.sleep(0.3)
                flush_print()

    except KeyboardInterrupt:
        print("\nKeluar.")

    finally:
        ser.close()

if __name__ == "__main__":
    main()
