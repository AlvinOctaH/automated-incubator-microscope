# 🔬 Automation Incubator Microscope

<div align="center">

![Project Status](https://img.shields.io/badge/Status-In%20Development-yellow?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20%7C%20Arduino-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**A custom 3-axis automated microscope stage for continuous long-term live-cell imaging, developed at NCKU.**

[Overview](#overview) · [Mechanical](#-mechanical) · [Electrical](#-electrical) · [Software](#-software)

</div>

---

## Overview

An automated XYZ microscope stage designed for continuous 24/7 brightfield imaging of biological samples (spheroids) in wellplates. Built around a Raspberry Pi 4 and Arduino Nano V3, the system enables unattended long-term live-cell imaging with motorized focus and sample positioning.

| Feature | Specification |
| :--- | :--- |
| Axes | X, Y, Z (independent translational) |
| Linear Resolution | 5 µm/step (full-step) |
| Travel (Z) | TBD (To Be Determined) |
| Motor Driver | DRV8825 |
| Controller | Arduino Nano V3 + Raspberry Pi 4 |
| Camera | Raspberry Pi HQ Camera (IMX477) |
| Target Sample | 96-well plate |
| Primary Material | PLA-CF |
| Operating Mode | Continuous 24/7 |

---

## 🔩 Mechanical

### 1. Components & Specs

### 2. Motion Calculation

#### Degrees of Freedom (DOF)

<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Kinematic%20%26%20Motion%20Analysis.gif" width="800"/>
</p>

Each axis provides exactly 1 translational DOF with no unintended rotational or parasitic motion, confirming proper constraint and assembly.

| Axis | DOF Type | Notes |
| :--- | :--- | :--- |
| X | 1 Translational | Stacked system |
| Y | 1 Translational | — |
| Z | 1 Translational | Focus axis |

#### Lead Screw Motion

- **Lead screw pitch:** 1 mm/rev  
- **Stepper motor:** 200 steps/rev, full-step (all axes)

**Theoretical linear resolution:**

$$
\text{Resolution} = \frac{\text{Lead Screw Pitch}}{\text{Steps per Revolution}} = \frac{1\ \text{mm}}{200 \times 1} = 0.005\ \text{mm} = 5\ \mu\text{m}
$$

**Required steps for full Z travel (9 mm gap between plates):**

$$
\text{Required Steps} = \frac{9\ \text{mm}}{5\ \mu\text{m}} = \frac{9000\ \mu\text{m}}{5\ \mu\text{m}} = 1800\ \text{steps}
$$

#### Interference Analysis

<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Inference%20Analysis.jpeg" width="800"/>
</p>

> ⚠️ **Note:** The interference analysis flags several overlaps in the CAD model. These occur within intentionally modeled precision components (linear rails, KFL08 bearing threaded regions) and are not physically relevant in real-world assembly. No functional collisions exist in the final design.

---

### 3. Material Comparison

Static load analysis was performed on the stage plate under gravity only (−Z, 9.81 m/s²). Two materials were evaluated: **PLA-CF** and **Aluminum 6061**.

#### A. PLA-CF

<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/PLA-CF_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/PLA-CF_02.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/PLA-CF_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/PLA-CF_4.png" width="500" height="400"/>
</p>

- Displacement contour dominated by **green regions** (~0.035–0.052 mm range)
- Deformation concentrated at upper stage plate and stepper motor mounting area
- Stepper motor self-weight is the dominant contributor to deflection
- Global sagging observed due to lower elastic modulus of PLA-CF

#### B. Aluminum 6061

<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Alumnium_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Aluminum_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Aluminum_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Aluminum_4.png" width="500" height="400"/>
</p>

- Displacement contour dominated by **dark blue regions** (<1 µm)
- Negligible deformation under gravity-only loading
- High stiffness effectively resists bending from stepper motor self-weight

#### Comparison Summary

<div align="center">

| Parameter | PLA-CF | Aluminum 6061 |
| :--- | :---: | :---: |
| Stiffness | Moderate | Very High |
| Max Deflection | ~54 µm | <1 µm |
| Structural Rigidity | Global sagging | Negligible bending |
| Focus Reliability | ⚠️ Not suitable for high magnification | ✅ Suitable for precision imaging |
| Verdict | Acceptable for non-critical parts | Recommended for structural parts |

</div>

#### Insight

PLA-CF was selected as the primary material due to significantly lower cost and ease of reprinting during design iteration. Although maximum deflection (~54 µm) is higher than Aluminum 6061 (<1 µm), this deformation remains well below the threshold that would affect imaging quality at the magnification used in this system. For a research prototype requiring frequent mechanical revisions, PLA-CF offers the best balance between structural adequacy and development speed.

---

### 4. Design Iteration

Structural analysis was conducted on motor brackets for all three axes. Each bracket was evaluated across two design iterations.

#### A. X Motor Bracket

<details>
<summary>Previous Version</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx0.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx0_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx0_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx0_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>New Version</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx1_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx1_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx1_4.png" width="500" height="400"/>
</p>
</details>

#### B. Y Motor Bracket

<details>
<summary>Previous Version</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety0.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety0_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety0_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety0_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>New Version</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety1_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety1_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety1_4.png" width="500" height="400"/>
</p>
</details>

#### C. Z Motor Bracket

<details>
<summary>Previous Version</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz0.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz0_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz0_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz0_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>New Version</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz1_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz1_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz1_4.png" width="500" height="400"/>
</p>
</details>

> 📝 **TBD:** Add max stress, safety factor, and design change rationale for each axis.

---

### 5. Imaging Calculation

#### Known Variables

| Variable | Symbol | Value | Source |
| :--- | :--- | :--- | :--- |
| Nominal tube length | L₀ | 160 mm | Objective spec |
| Nominal magnification | M₀ | 10x | Objective spec |
| Sensor width | Sw | 6.287 mm | IMX477 datasheet |
| Sensor height | Sh | 4.712 mm | IMX477 datasheet |
| Sensor resolution (H × V) | Rw × Rh | 4056 × 3040 px | IMX477 datasheet |
| Pixel size | p | 1.55 × 1.55 µm | IMX477 datasheet |

> **Verification:** `Sw = p × Rw = 1.55µm × 4056 = 6.287mm` ✅

#### Formulas

**1. Actual Magnification at a Given Tube Length**

$$M_{actual} = M_0 \times \frac{L_{actual}}{L_0}$$

> ⚠️ This formula is an approximation valid at the nominal tube length (160mm). Any deviation introduces spherical aberrations — empirical validation is required for non-nominal tube lengths.

**2. Field of View**

$$FOV_{horizontal} = \frac{S_w}{M_{actual}} \qquad FOV_{vertical} = \frac{S_h}{M_{actual}}$$

**3. Limiting FOV (circular samples)**

$$FOV_{limiting} = FOV_{vertical} = \frac{S_h}{M_{actual}}$$

**4. Required Tube Length for a Target FOV**

$$L_{target} = \frac{S_h \times L_0}{M_0 \times FOV_{target}}$$

**5. Empirical Scale (known bead size)**

$$\mu m/pixel = \frac{d_{bead,real}}{d_{bead,pixel}} \qquad M_{actual} = \frac{S_w}{FOV_{horizontal}} \times 1000$$

**6. Empirical FOV Ratio (unknown bead size)**

$$\frac{FOV_1}{FOV_2} = \frac{L_2}{L_1} = \frac{d_{bead,px,2}}{d_{bead,px,1}}$$

#### Worked Example — 96-well Plate

**Target:** Image an entire single well (diameter = 9 mm)

$$FOV_{vertical,160} = \frac{4.712}{10} = 0.4712\ \text{mm} = 471.2\ \mu\text{m}$$

$$L_{target} = 160 \times \frac{471.2}{9000} \approx 8.4\ \text{mm} \quad \Rightarrow \quad M_{actual} = 10 \times \frac{8.4}{160} = 0.525\text{x}$$

$$FOV_{vertical} = \frac{4.712}{0.525} \approx 9.0\ \text{mm}\ ✅ \qquad FOV_{horizontal} = \frac{6.287}{0.525} = 11.97\ \text{mm}$$

| Tube Length | Magnification | FOV Horizontal | FOV Vertical | Fits 9mm well? |
| :--- | :--- | :--- | :--- | :--- |
| 160 mm | 10x | 628.7 µm | 471.2 µm | ❌ |
| 130 mm | 8.125x | 774 µm | 580 µm | ❌ |
| 9 mm | 0.5625x | 11.18 mm | 8.38 mm | ⚠️ nearly |
| **8.4 mm** | **0.525x** | **11.97 mm** | **9.00 mm** | **✅** |

---

### 6. Thermal Consideration

Thermal images of each stepper motor and the well plate under 24/7 operating conditions:

<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20X.jpeg" width="200"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20Y.jpeg" width="200"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20Z.jpeg" width="200"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Wellplate.jpeg" width="200"/>
</p>

> 📝 **TBD:** Add peak temperatures per motor, wellplate temperature, and acceptable operating range.

---

### 7. Engineering Drawing

> 🚧 **In progress** — engineering drawings and GD&T specifications to be added.

---

### 8. Mechanical Insight

> 📝 **TBD:** Add final design decisions and rationale per subsection.

---

## ⚡ Electrical

### 1. Components & BOM

| Component | Part Number | Specification | Quantity |
| :--- | :--- | :--- | :---: |
| PSU (Motor) | Meanwell LRS-100-12 | 12V, 8.3A | 1 |
| PSU (Logic) | Meanwell LRS-35-5 | 5V, 7A | 1 |
| Motor Driver | DRV8825 | Up to 1/32 microstepping | 3 |
| Stepper Motor | NEMA14 42-40 | 1.2A, 200 steps/rev | 3 |
| MCU | Arduino Nano V3 | ATmega328P, 5V logic | 1 |
| SBC | Raspberry Pi 4 | 3.3V logic | 1 |
| Level Shifter | Bidirectional LLC | 3.3V ↔ 5V | 1 |
| AC Input | IEC C14 Receptacle | — | 1 |
| Fuse (AC) | — | 3A Slow Blow | 1 |
| Fuse (Motor) | — | 5A | 1 |
| Polyfuse (Logic) | — | 3A Resettable | 1 |

### 2. Schematic

> 📝 **TBD:** Add schematic images here.

### 3. Calculations

> 📝 **TBD:** Add power budget, current calculations, and signal flow description.

### 4. Electrical Insight

> 📝 **TBD:** Add design decisions — e.g. dual PSU rationale, ground separation strategy, driver protection.

---

## 💻 Software

### 1. Architecture

```
software/
├── firmware/           # Arduino Nano — step/dir motor control
│   └── main.ino
├── control/            # Raspberry Pi — high-level control & GUI
│   ├── main.py
│   └── serial_comm.py
└── calibration/        # Stage calibration scripts
    └── calibrate.py
```

### 2. GUI

> 🚧 **In progress**

### 3. Data Management

> 🚧 **In progress**

### 4. Software Insight

> 📝 **TBD:** Add design decisions — e.g. RPi vs Arduino task separation, communication protocol, data pipeline.

---

## 📁 Repository Structure

```
Automation-Incubator-Microscope/
├── src/                    # Images and media assets
├── mechanical/             # CAD files and FEA results
│   ├── stage-plate/
│   ├── motor-brackets/
│   └── drawings/
├── electrical/             # Schematics and BOM
├── software/               # Firmware and control scripts
├── docs/                   # Additional documentation
└── README.md
```
