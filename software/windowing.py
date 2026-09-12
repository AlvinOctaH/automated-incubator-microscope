"""
Spheroid Microscope Image — Windowing Post-Processing
Interactive slider to find optimal Level (L) and Window (W) values.
Once happy with the result, note the L and W values for use in Raspberry Pi pipeline.

Usage:
    python windowing.py                        # opens file dialog
    python windowing.py path/to/image.jpg      # opens specific image
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from PIL import Image
import os

# ── Load image ──────────────────────────────────────────────────────────────

def load_image(path):
    img = Image.open(path).convert("L")  # convert to grayscale
    return np.array(img, dtype=np.float32)

def get_image_path():
    if len(sys.argv) > 1:
        return sys.argv[1]
    # fallback: try tkinter file dialog
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(
            title="Select microscope image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.tif *.tiff")]
        )
        root.destroy()
        return path if path else None
    except Exception:
        print("No image path provided. Usage: python windowing.py <image_path>")
        return None

# ── Windowing transform ──────────────────────────────────────────────────────

def apply_windowing(img, L, W):
    """
    Piecewise linear windowing:
        I_out = 0          if I <= L - W/2
        I_out = 255        if I >= L + W/2
        I_out = linear     otherwise
    """
    low  = L - W / 2
    high = L + W / 2
    out = np.clip((img - low) / (high - low) * 255, 0, 255)
    return out.astype(np.uint8)

# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    path = get_image_path()
    if path is None or not os.path.exists(path):
        print("Image not found.")
        sys.exit(1)

    img = load_image(path)
    h, w = img.shape

    # Initial values — start at full range, user can narrow down
    init_L = 128
    init_W = 200

    processed = apply_windowing(img, init_L, init_W)

    # ── Layout ──
    fig = plt.figure(figsize=(14, 7))
    fig.suptitle(f"Windowing — {os.path.basename(path)}", fontsize=11)

    ax_orig    = fig.add_axes([0.02, 0.25, 0.30, 0.65])
    ax_proc    = fig.add_axes([0.35, 0.25, 0.30, 0.65])
    ax_hist    = fig.add_axes([0.68, 0.25, 0.30, 0.65])

    ax_slider_L = fig.add_axes([0.10, 0.12, 0.75, 0.03])
    ax_slider_W = fig.add_axes([0.10, 0.07, 0.75, 0.03])
    ax_save     = fig.add_axes([0.40, 0.01, 0.20, 0.04])

    # ── Original ──
    ax_orig.imshow(img, cmap="gray", vmin=0, vmax=255)
    ax_orig.set_title("Original")
    ax_orig.axis("off")

    # ── Processed ──
    im_proc = ax_proc.imshow(processed, cmap="gray", vmin=0, vmax=255)
    ax_proc.set_title("Windowed")
    ax_proc.axis("off")

    # ── Histogram ──
    ax_hist.hist(img.ravel(), bins=256, range=(0, 255), color="gray", alpha=0.7)
    ax_hist.set_xlim(0, 255)
    ax_hist.set_title("Intensity Histogram")
    ax_hist.set_xlabel("Pixel intensity")
    ax_hist.set_ylabel("Count")
    line_low  = ax_hist.axvline(init_L - init_W/2, color="blue",  linestyle="--", label="Low")
    line_high = ax_hist.axvline(init_L + init_W/2, color="red",   linestyle="--", label="High")
    line_L    = ax_hist.axvline(init_L,             color="green", linestyle="-",  label="Level")
    ax_hist.legend(fontsize=8)

    # ── Info text ──
    info_text = ax_proc.text(
        0.02, 0.02, f"L={init_L}  W={init_W}",
        transform=ax_proc.transAxes,
        color="yellow", fontsize=9,
        bbox=dict(facecolor="black", alpha=0.5, pad=2)
    )

    # ── Sliders ──
    slider_L = Slider(ax_slider_L, "Level (L)", 0, 255, valinit=init_L, valstep=1, color="green")
    slider_W = Slider(ax_slider_W, "Window (W)", 1, 255, valinit=init_W, valstep=1, color="steelblue")

    def update(val):
        L = int(slider_L.val)
        W = int(slider_W.val)
        result = apply_windowing(img, L, W)
        im_proc.set_data(result)
        line_low.set_xdata([L - W/2, L - W/2])
        line_high.set_xdata([L + W/2, L + W/2])
        line_L.set_xdata([L, L])
        info_text.set_text(f"L={L}  W={W}")
        fig.canvas.draw_idle()

    slider_L.on_changed(update)
    slider_W.on_changed(update)

    # ── Save button ──
    btn_save = Button(ax_save, "Save Result", color="lightgreen")

    def save(event):
        L = int(slider_L.val)
        W = int(slider_W.val)
        result = apply_windowing(img, L, W)
        base = os.path.splitext(os.path.basename(path))[0]
        out_path = os.path.join(os.path.dirname(path), f"{base}_L{L}_W{W}.png")
        Image.fromarray(result).save(out_path)
        print(f"✅ Saved: {out_path}")
        print(f"   → Use these values in Raspberry Pi pipeline: L={L}, W={W}")
        ax_save.set_facecolor("lightblue")
        btn_save.label.set_text("Saved!")
        fig.canvas.draw_idle()

    btn_save.on_clicked(save)

    plt.show()

if __name__ == "__main__":
    main()
