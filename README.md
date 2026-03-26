# 🔬 Automation Incubator Microscope

<div align="center">

![Project Status](https://img.shields.io/badge/Status-In%20Development-yellow?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Raspberry%20Pi%20%7C%20Arduino-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**A custom 3-axis automated linear stage for microscopy applications, developed at NCKU.**

[Overview](#overview) · [Mechanical](#-mechanical-documentation) · [Electrical](#-electrical-documentation) · [Getting Started](#-getting-started) · [Contributing](#-contributing)

</div>

---

## Overview

This project documents the development of a custom motorized XYZ linear stage integrated with an incubator microscope setup. The system enables automated sample positioning for long-term live-cell imaging experiments.

| Feature | Specification |
| :--- | :--- |
| Axes | X, Y, Z (independent translational) |
| Linear Resolution | 5 µm/step (full-step) |
| Travel (Z) | 9 mm |
| Motor Driver | DRV8825 |
| Controller | Arduino Nano + Raspberry Pi 3A+ |
| Primary Material | PLA-CF / Aluminum 6061 |

---

## 🔩 Mechanical Documentation

### Kinematic & Motion Analysis

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

### Structural Rigidity

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

#### Material Comparison Summary

<div align="center">

| Parameter | PLA-CF | Aluminum 6061 |
| :--- | :---: | :---: |
| Stiffness | Moderate | Very High |
| Max Deflection | ~54 µm | <1 µm |
| Structural Rigidity | Global sagging | Negligible bending |
| Focus Reliability | ⚠️ Not suitable for high magnification | ✅ Suitable for precision imaging |
| Verdict | Acceptable for non-critical parts | **Recommended for structural parts** |

</div>

---

### Motor Bracket Analysis

Structural analysis was conducted on motor brackets for all three axes. Each bracket was evaluated in two design iterations.

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

> 📝 **Motor Bracket Summary:** *(to be completed — add max stress, safety factor, and design change rationale for each axis)*

---

### Vibration Consideration

> 🚧 **In progress** — modal analysis and vibration isolation strategy to be documented.

---

### Thermal Consideration

Thermal images of each stepper motor and the well plate under operating conditions:

<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20X.jpeg" width="200"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20Y.jpeg" width="200"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20Z.jpeg" width="200"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Wellplate.jpeg" width="200"/>
</p>

> 📝 **Add here:** peak temperatures recorded, acceptable operating range, any heat mitigation measures taken.

---

### Drawing & Tolerance

> 🚧 **In progress** — engineering drawings and GD&T specifications to be added.

---

### Imaging Calculation
#### Known Variables
 
| Variable | Symbol | Value | Source |
| :--- | :--- | :--- | :--- |
| Nominal tube length | L₀ | 160 mm | Objective spec |
| Nominal magnification | M₀ | 10x | Objective spec |
| Sensor width | Sw | 6.287 mm | IMX477 datasheet |
| Sensor height | Sh | 4.712 mm | IMX477 datasheet |
| Sensor resolution (H × V) | Rw × Rh | 4056 × 3040 px | IMX477 datasheet |
| Pixel size | p | 1.55 × 1.55 µm | IMX477 datasheet |
 
> **Verification:** Sensor size can be independently verified as:
> `Sw = p × Rw = 1.55µm × 4056 = 6.287mm` ✅
 
#### Formulas
 
**1. Actual Magnification at a Given Tube Length**
 
When tube length deviates from nominal, magnification scales linearly:
 
$$M_{actual} = M_0 \times \frac{L_{actual}}{L_0}$$
 
> ⚠️ This formula is an approximation valid at the nominal tube length (160mm). Any deviation from the nominal tube length introduces spherical aberrations and degrades image quality ([Evident Scientific / Olympus MicroscopyU](https://evidentscientific.com/en/microscope-resource/knowledge-hub/anatomy/tubelength)). The degree of degradation increases with deviation — empirical validation is required for non-nominal tube lengths.
 
**2. Field of View at a Given Magnification**
 
FOV is calculated separately for horizontal and vertical axes:
 
$$FOV_{horizontal} = \frac{S_w}{M_{actual}}$$
 
$$FOV_{vertical} = \frac{S_h}{M_{actual}}$$
 
**3. Limiting FOV (for circular samples like well plates)**
 
Since the sensor is rectangular but well plates are circular, the **vertical FOV is the limiting dimension** (smaller side):
 
$$FOV_{limiting} = FOV_{vertical} = \frac{S_h}{M_{actual}}$$
 
If `FOV_vertical ≥ well diameter`, then the entire well fits in frame.
 
**4. Required Tube Length for a Target FOV**
 
To find the tube length needed to achieve a specific FOV:
 
$$L_{target} = L_0 \times \frac{FOV_{ref}}{FOV_{target}}$$
 
Where `FOV_ref` is the FOV at the reference tube length (L₀). Or directly from sensor size:
 
$$L_{target} = \frac{S_h \times L_0}{M_0 \times FOV_{target}}$$
 
**5. Empirical Scale (if actual bead size is known)**
 
If the real diameter of a microbead is known from its datasheet:
 
$$\mu m/pixel = \frac{d_{bead,real}}{d_{bead,pixel}}$$
 
$$FOV_{horizontal} = \frac{d_{bead,real}}{d_{bead,pixel}} \times R_w$$
 
$$FOV_{vertical} = \frac{d_{bead,real}}{d_{bead,pixel}} \times R_h$$
 
$$M_{actual} = \frac{S_w}{FOV_{horizontal}} \times 1000$$
 
> Note: multiply by 1000 to reconcile units (Sw in mm, FOV in µm).
 
**6. Empirical FOV Ratio (without knowing bead size)**
 
If bead size is unknown but the same beads are imaged at two different tube lengths, the FOV ratio can be derived purely from pixel measurements:
 
$$\frac{FOV_1}{FOV_2} = \frac{L_2}{L_1} = \frac{d_{bead,px,2}}{d_{bead,px,1}}$$
 
This allows prediction of tube length for a target FOV using only pixel measurements, without knowing the real bead size.
 
#### Worked Example — Well Plate 96
 
**Target:** Image an entire single well of a 96-well plate.  
**Well diameter:** 9 mm = 9000 µm
 
**Step 1 — FOV at reference (160mm, 10x):**
 
$$FOV_{vertical,160} = \frac{4.712\ \text{mm}}{10} = 0.4712\ \text{mm} = 471.2\ \mu\text{m}$$
 
**Step 2 — Required tube length:**
 
$$L_{target} = 160 \times \frac{471.2}{9000} \approx 8.4\ \text{mm}$$
 
**Step 3 — Magnification at that tube length:**
 
$$M_{actual} = 10 \times \frac{8.4}{160} = 0.525\text{x}$$
 
**Step 4 — Verify FOV:**
 
$$FOV_{vertical} = \frac{4.712\ \text{mm}}{0.525} = 8.97\ \text{mm} \approx 9\ \text{mm}\ ✅$$
 
$$FOV_{horizontal} = \frac{6.287\ \text{mm}}{0.525} = 11.97\ \text{mm}$$
 
> The well fits fully in frame vertically. Horizontal FOV is wider (11.97mm), providing extra margin.
 
#### Summary Table
 
| Tube Length | Magnification | FOV Horizontal | FOV Vertical | Fits 9mm well? |
| :--- | :--- | :--- | :--- | :--- |
| 160 mm | 10x | 628.7 µm | 471.2 µm | ❌ |
| 130 mm | 8.125x | 774 µm | 580 µm | ❌ |
| 9 mm | 0.5625x | 11.18 mm | 8.38 mm | ⚠️ nearly |
| **8.4 mm** | **0.525x** | **11.97 mm** | **9.00 mm** | **✅** |



---

## ⚡ Electrical Documentation

### System Architecture

#### Electrical Block Diagram

```mermaid
flowchart TD

%% ================= AC FRONT END =================
A[AC Mains 110VAC] --> B[Fuse 3A Slow Blow]
B --> C[IEC C14 EMI Filter]
C --> TB[AC Terminal Block Distribution]

%% ================= PSU DISTRIBUTION =================
TB --> PSU1[MEAN WELL LRS-100-12 12V 8.5A]
TB --> PSU2[MEAN WELL RD-35A 5V 4A]

%% ================= MOTOR DOMAIN =================
PSU1 --> FM[Fuse 5A Motor Rail]
FM --> M12V[12V Motor BUS]

M12V --> SD1[DRV8825 X + 100uF + 0.1uF + TVS 18V]
M12V --> SD2[DRV8825 Y + 100uF + 0.1uF + TVS 18V]
M12V --> SD3[DRV8825 Z + 100uF + 0.1uF + TVS 18V]

SD1 --> SM1[Stepper X 1.2A]
SD2 --> SM2[Stepper Y 1.2A]
SD3 --> SM3[Stepper Z 1.2A]

%% ================= LOGIC DOMAIN =================
PSU2 --> FL[Fuse 3A Logic Rail]
FL --> L5V[5V_LOGIC BUS]

L5V --> |Polyfuse 2A + 470uF Bulk| PI[Raspberry Pi 3A+]
L5V --> ARD[Arduino Nano]

%% ================= LEVEL SHIFT =================
PI <-->|3.3V TX/RX| LS[Logic Level Shifter]
ARD <-->|5V TX/RX| LS

%% ================= CONTROL =================
ARD -->|STEP/DIR| SD1
ARD -->|STEP/DIR| SD2
ARD -->|STEP/DIR| SD3

%% ================= GROUND STRATEGY =================
PSU1 --> SG[Star Ground Point]
PSU2 --> SG
M12V --> SG
L5V --> SG
```

#### Component List

| Component | Part Number | Specification | Quantity |
| :--- | :--- | :--- | :---: |
| PSU (Motor) | MEAN WELL LRS-100-12 | 12V, 8.5A | 1 |
| PSU (Logic) | MEAN WELL RD-35A | 5V, 4A | 1 |
| Motor Driver | DRV8825 | 1/32 microstepping | 3 |
| Stepper Motor | — | 1.2A, 200 steps/rev | 3 |
| MCU | Arduino Nano | 5V logic | 1 |
| SBC | Raspberry Pi 3A+ | 3.3V logic | 1 |
| Level Shifter | — | 3.3V ↔ 5V | 1 |
| EMI Filter | IEC C14 | — | 1 |

> 📝 **Theoretical approach section:** *(to be completed — add signal flow description, control loop explanation, communication protocol)*

---

## 💻 Software Documentation

> 🚧 **In progress** — firmware (Arduino) and control software (Raspberry Pi) to be documented.

### Planned Structure

```
software/
├── firmware/           # Arduino Nano — step/dir control
│   └── main.ino
├── control/            # Raspberry Pi — high-level control
│   ├── main.py
│   └── serial_comm.py
└── calibration/        # Stage calibration scripts
    └── calibrate.py
```

---

## 🚀 Getting Started

> 🚧 **In progress** — assembly guide and setup instructions to be added.

### Prerequisites

- Arduino IDE ≥ 2.x
- Python ≥ 3.9
- Raspberry Pi OS (64-bit)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/AlvinOctaH/Automation-Incubator-Microscope.git
cd Automation-Incubator-Microscope

# Install Python dependencies
pip install -r requirements.txt

# Flash Arduino firmware
# Open firmware/main.ino in Arduino IDE and upload to Nano
```

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

---

## 🗺️ Roadmap

- [x] Kinematic & motion analysis
- [x] Structural rigidity analysis (stage plate)
- [x] Motor bracket FEA (X, Y, Z)
- [x] Electrical architecture diagram
- [ ] Vibration analysis
- [ ] Engineering drawings & tolerances
- [ ] Firmware documentation
- [ ] Control software documentation
- [ ] Assembly guide
- [ ] Calibration procedure

---

## 👤 Author

**Alvin Octa H**  
Internship @ National Cheng Kung University (NCKU)  
Department of *(your department)*  

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">
<sub>Built with ☕ during internship at NCKU · Taiwan</sub>
</div>
