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
| Component | Specification | Quantity |
| :--- | :--- | :---: |
| Stepper Motor | NEMA17 42-40, 1.8°/step, ~40 N·cm holding torque | 3 |
| Lead Screw | T8, 1 mm pitch | 3 |
| Anti-backlash Nut | 8 mm | 3 |
| Flexible Coupler | 5 mm to 8 mm | 3 |
| Linear Rail | MGN12H | 3 |
| Aluminum Extrusion | Alpro, various lengths | — |

### 2. Motion Calculation

#### Degrees of Freedom (DOF)

<p align="center">
  <img src="assets/kinematik&motion.gif" width="800"/>
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
  <img src="assets/inference_analysis.jpeg" width="800"/>
</p>

> ⚠️ **Note:** The interference analysis flags several overlaps in the CAD model. These occur within intentionally modeled precision components (linear rails, KFL08 bearing threaded regions) and are not physically relevant in real-world assembly. No functional collisions exist in the final design.

---

### 3. Material Comparison

Static load analysis was performed on the stage plate under gravity only
(−Z, 9.81 m/s²). Three materials were evaluated: **PLA-CF**, **PLA-Basic**,
and **Aluminum 6061**.

**Displacement** shows how much the structure physically deforms under load —
lower values indicate a stiffer, more stable platform, which is critical for
maintaining focus consistency during imaging.

**Von Mises Stress** shows the internal stress distribution across the
structure. Results dominated by blue contour across all three materials
indicate that stress levels remain well within safe limits throughout the
structural body under gravity-only loading.

**Safety Factor** is derived from the ratio of material yield strength to
local von Mises stress. Values above 2 are generally considered acceptable
in engineering practice. The minimum value is read from the Inventor SF
contour plot — peak stress occurs only at localized concentration points,
while the majority of the structure maintains a high safety margin as
confirmed by the blue-dominated contour.

> ⚠️ Note: Peak displacement values include contribution from motor assembly
> motion. Structural frame comparison is best assessed from the color contour
> distribution in the images above.

#### Material Properties

| Property | PLA-CF | PLA-Basic | Aluminum 6061 |
| :--- | :---: | :---: | :---: |
| Young Modulus (MPa) | 2790 | 2750 | Default Autodesk Inventor |
| Poisson Ratio | 0.33 | 0.36 | Default Autodesk Inventor |
| Shear Modulus (MPa) | 1048 | 1010 | Default Autodesk Inventor |
| Yield Strength (MPa) | 38 | 35 | Default Autodesk Inventor |

#### A. PLA-CF

<details>
<summary>Displacement</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>Von Mises Stress</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF-VMS_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF-VMS_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF-VMS_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF-VMS_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>Safety Factor</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF-SF_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF-SF_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF-SF_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-CF-SF_4.png" width="500" height="400"/>
</p>
</details>

- Max displacement: **0.089 mm**
- Max von Mises stress: **51.42 MPa** — stress distribution dominated by blue contour, structure is safe throughout
- Min safety factor: **4.03** — well above acceptable threshold
- Carbon fiber reinforcement improves stiffness compared to PLA-Basic

#### B. PLA-Basic

<details>
<summary>Displacement</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>Von Mises Stress</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic-VMS_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic-VMS_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic-VMS_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic-VMS_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>Safety Factor</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic-SF_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic-SF_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic-SF_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/PLA-Basic-SF_4.png" width="500" height="400"/>
</p>
</details>

- Max displacement: **0.11 mm** — highest among all three materials
- Max von Mises stress: **68.52 MPa** — stress distribution dominated by blue contour, structure is safe throughout
- Min safety factor: **3.02** — above acceptable threshold but lowest among three materials
- Higher deformation due to absence of carbon fiber reinforcement

#### C. Aluminum 6061

<details>
<summary>Displacement</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>Von Mises Stress</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum-VMS_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum-VMS_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum-VMS_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum-VMS_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>Safety Factor</summary>
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum-SF_1.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum-SF_2.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum-SF_3.png" width="500" height="400"/>
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/mechanical/stage-plate/Alum-SF_4.png" width="500" height="400"/>
</p>
</details>

- Max displacement: **~0.017 mm** — lowest among all three materials
- Max von Mises stress: **50.21 MPa** — stress distribution dominated by blue contour, structure is safe throughout
- Min safety factor: **4.12** — highest among three materials
- Negligible deformation under gravity-only loading


#### Comparison Summary

<div align="center">

| Parameter | PLA-Basic | PLA-CF | Aluminum 6061 |
| :--- | :---: | :---: | :---: |
| Max Displacement | 0.11 mm | 0.089 mm | ~0.017 mm |
| Max Von Mises Stress | 68.52 MPa | 51.42 MPa | 50.21 MPa |
| Min Safety Factor | 3.02 | 4.03 | 4.12 |
| Stress Distribution | ✅ Safe (blue) | ✅ Safe (blue) | ✅ Safe (blue) |
| Stiffness | Low | Moderate | Very High |
| Cost | Low | Medium | High |
| Printability | ✅ Easy | ✅ Easy | ❌ Requires machining |
| Verdict | ⚠️ Acceptable | ✅ Selected | Reference only |

</div>

#### Insight

All three materials show safe stress distribution under gravity-only loading, with minimum safety factors well above 2 across the entire structure. Aluminum 6061 offers the best mechanical performance — lowest displacement (~0.017 mm) and highest safety factor (4.12) — but requires CNC machining which significantly increases cost and lead time for an iterative research prototype. PLA-Basic has the lowest safety factor (3.02) and highest displacement (0.11 mm) due to the absence of carbon fiber reinforcement. PLA-CF was selected as the optimal material, offering a higher safety factor than PLA-Basic (4.03), lower displacement (0.089 mm), and the same ease of 3D printing — making it the most practical choice for this stage of development.

---

### 4. Design Iteration

Structural analysis was conducted on motor brackets for all three axes. Each bracket was evaluated across two design iterations.

#### A. X Motor Bracket

<details>
<summary>Previous Version</summary>
<p align="center">
  <img src="assets/stress_analysis_results/bracketx0.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketx0_2.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketx0_3.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketx0_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>New Version</summary>
<p align="center">
  <img src="assets/stress_analysis_results/bracketx1.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketx1_2.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketx1_3.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketx1_4.png" width="500" height="400"/>
</p>
</details>

#### B. Y Motor Bracket

<details>
<summary>Previous Version</summary>
<p align="center">
  <img src="assets/stress_analysis_results/brackety0.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/brackety0_2.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/brackety0_3.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/brackety0_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>New Version</summary>
<p align="center">
  <img src="assets/stress_analysis_results/brackety1.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/brackety1_2.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/brackety1_3.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/brackety1_4.png" width="500" height="400"/>
</p>
</details>

#### C. Z Motor Bracket

<details>
<summary>Previous Version</summary>
<p align="center">
  <img src="assets/stress_analysis_results/bracketz0.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketz0_2.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketz0_3.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketz0_4.png" width="500" height="400"/>
</p>
</details>

<details>
<summary>New Version</summary>
<p align="center">
  <img src="assets/stress_analysis_results/bracketz1.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketz1_2.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketz1_3.png" width="500" height="400"/>
  <img src="assets/stress_analysis_results/bracketz1_4.png" width="500" height="400"/>
</p>
</details>

> 📝 **TBD:** Add max stress, safety factor, and design change rationale for each axis.

---

### 5. Imaging System Design
 
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
 
#### Formulas & Derivations
 
**1. Actual Magnification at a Given Tube Length**
 
Magnification in a lens system is defined as the ratio of image distance to object distance. Since the sample is always fixed at the objective's focal plane, only the image distance (tube length) changes. Therefore magnification scales linearly with tube length:
 
$$M_{actual} = M_0 \times \frac{L_{actual}}{L_0}$$
 
> ⚠️ Valid as an approximation near the nominal tube length (160mm). Larger deviations introduce spherical aberrations — empirical validation is required.
 
**2. Field of View**
 
Rearranging the definition of magnification (`M = image size / object size`), the real-world size captured by the sensor is:
 
$$FOV_{horizontal} = \frac{S_w}{M_{actual}} \qquad FOV_{vertical} = \frac{S_h}{M_{actual}}$$
 
**3. Limiting FOV (circular samples)**
 
The sensor is rectangular but wellplates are circular. The vertical axis (shorter side) is the limiting dimension:
 
$$FOV_{limiting} = FOV_{vertical} = \frac{S_h}{M_{actual}}$$
 
**4. Required Tube Length for a Target FOV**
 
Combining formulas 1 and 2 and solving for tube length:
 
$$L_{target} = \frac{S_h \times L_0}{M_0 \times FOV_{target}}$$
 
**5. Empirical Scale (known bead size)**
 
If the real diameter of a reference bead is known, pixel scale and FOV can be derived directly from image measurements:
 
$$\mu m/pixel = \frac{d_{bead,real}}{d_{bead,pixel}} \qquad M_{actual} = \frac{S_w}{FOV_{horizontal}} \times 1000$$
 
**6. Empirical FOV Ratio (unknown bead size)**
 
If bead size is unknown but the same beads are imaged at two different tube lengths, the FOV ratio can be derived purely from pixel measurements — no real size needed:
 
$$\frac{FOV_1}{FOV_2} = \frac{L_2}{L_1} = \frac{d_{bead,px,2}}{d_{bead,px,1}}$$
 
#### Tube Length Selection — 96-well Plate (well diameter = 9 mm)
 
Five tube lengths were selected for empirical testing, each with a distinct optical rationale:
 
| # | Tube Length | Magnification | FOV Horizontal | FOV Vertical | Rationale |
| :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | 160 mm | 10x | 628.7 µm | 471.2 µm | Nominal objective spec — baseline reference |
| 2 | 8.4 mm | 0.525x | 11.97 mm | 9.00 mm | FOV vertical = 9mm — fits entire well height |
| 3 | 11.2 mm | 0.70x | 8.98 mm | 6.73 mm | FOV horizontal = 9mm — fits entire well width |
| 4 | 84.2 mm | 5.26x | 1.20 mm | 0.90 mm | Midpoint between nominal and shortest — gradual aberration check |
| 5 | 64 mm | 4x | 1.57 mm | 1.18 mm | 4x magnification — evaluate mid-range image quality |
 
**Derivations:**
 
$$L_2 = \frac{S_h \times L_0}{M_0 \times FOV_{target}} = \frac{4.712 \times 160}{10 \times 9} \approx 8.4\ \text{mm}$$
 
$$L_3 = \frac{S_w \times L_0}{M_0 \times FOV_{target}} = \frac{6.287 \times 160}{10 \times 9} \approx 11.2\ \text{mm}$$
 
$$L_4 = \frac{8.4 + 160}{2} = 84.2\ \text{mm}$$
 
$$L_5 = \frac{4}{10} \times 160 = 64\ \text{mm}$$
 
#### Imaging Validation

Imaging validation was conducted in two stages: first using microbeads as a controlled reference target to evaluate optical performance across tube lengths, then using spheroids as the actual biological sample to confirm suitability for long-term live-cell imaging.

---

**Reference — Professional Lab Microscope**

Images captured using a professional laboratory microscope as ground truth reference for image quality comparison.

<table>
  <tr>
    <th align="center">Magnification</th>
    <th align="center">Image</th>
  </tr>
  <tr>
    <td align="center">4x</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/professional_microsope/using4x_microscope.jpg" width="200"/></td>
  </tr>
  <tr>
    <td align="center">10x</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/professional_microsope/using10x_microscope.jpg" width="200"/></td>
  </tr>
</table>

---

##### Stage 1 — Microbead Imaging

Microbeads were used as a controlled reference target to characterize optical performance across tube lengths. Each tube length was tested at two objective configurations (10x and 4x) to evaluate sharpness, chromatic aberration, and overall image quality before proceeding to biological samples.

###### 🔬 Objective Lens 10x

<table>
  <tr>
    <th align="center">#</th>
    <th>Tube Length</th>
    <th align="center">Microbeads</th>
    <th align="center">Microbeads + Light</th>
    <th>Notes</th>
  </tr>
  <tr>
    <td align="center">1</td>
    <td>160 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/160mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/160mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">2</td>
    <td>8.4 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/8.4mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/8.4mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">3</td>
    <td>11.2 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/11.2mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/11.2mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">4</td>
    <td>84.2 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/84.2mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/84.2mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">5</td>
    <td>64 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/64mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/64mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">6</td>
    <td>72 mm (4.5x Magnification)</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/72mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/72mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">7</td>
    <td>80 mm (5x Magnification)</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/80mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/10x/80mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
</table>

---

###### 🔬 Objective Lens 4x

<table>
  <tr>
    <th align="center">#</th>
    <th>Tube Length</th>
    <th align="center">Microbeads</th>
    <th align="center">Microbeads + Light</th>
    <th>Notes</th>
  </tr>
  <tr>
    <td align="center">1</td>
    <td>160 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/160mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/160mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">2</td>
    <td>8.4 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/8.4mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/8.4mm_with_light.jpg?raw=true" width="200"/></td>
    <td>Out of focus at this tube length with 4x objective — the combination of short tube length and lower base magnification places the image plane outside the usable focus range.</td>
  </tr>
  <tr>
    <td align="center">3</td>
    <td>11.2 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/11.2mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/11.2mm_with_light.jpg?raw=true" width="200"/></td>
    <td>Out of focus at this tube length with 4x objective — same constraint as 8.4 mm. These two tube lengths are outside the practical operating range for the 4x objective.</td>
  </tr>
  <tr>
    <td align="center">4</td>
    <td>84.2 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/84.2mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/84.2mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">5</td>
    <td>64 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/64mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/64mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">6</td>
    <td>72 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/72mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/72mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
  <tr>
    <td align="center">7</td>
    <td>80 mm</td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/80mm.jpg?raw=true" width="200"/></td>
    <td align="center"><img src="assets/imaging_results/data_microbeads/4x/80mm_with_light.jpg?raw=true" width="200"/></td>
    <td>TBD</td>
  </tr>
</table>

---

##### Stage 2 — Spheroid Imaging

> 🚧 **In progress** — spheroid imaging results to be added after biological sample testing.

Images will be captured at the selected tube length(s) from Stage 1 using actual spheroid samples in a 96-well plate. Results will include both 10x and 4x objective configurations.

###### 🔬 Objective Lens 10x

> 📝 **TBD:** Add spheroid images at selected tube length(s).

###### 🔬 Objective Lens 4x

> 📝 **TBD:** Add spheroid images at selected tube length(s).

---

#### Insight

> 📝 **TBD:** Add after empirical testing — which tube length gives the best balance of FOV, sharpness, and aberration for spheroid imaging.

###

---

### 6. Thermal Consideration

Thermal images of each stepper motor and the well plate under 24/7 operating conditions:

<p align="center">
  <img src="assets/thermal_results/stp_mtr_x.jpeg" width="200"/>
  <img src="assets/thermal_results/stp_mtr_y.jpeg" width="200"/>
  <img src="assets/thermal_results/stp_mtr_z.jpeg" width="200"/>
  <img src="assets/thermal_results/wellplate.jpeg" width="200"/>
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

### 1. Components & Specs

| Component | Part Number | Specification | Quantity |
| :--- | :--- | :--- | :---: |
| PSU (Logic) | Meanwell LRS-35-5 | 5V, 7A | 1 |
| PSU (Motor) | Meanwell LRS-100-12 | 12V, 8.3A | 1 |
| Stepper Motor | NEMA17 42-40 | 1.8°/step, 200 steps/rev | 3 |
| Motor Driver | DRV8825 (Pololu Breakout) | Up to 1/32 microstepping | 3 |
| TVS Diode | D_TVS 18V | Motor back-EMF protection | 3 |
| MCU | Arduino Nano V3 | ATmega328P, 5V logic | 1 |
| SBC | Raspberry Pi 4 | 3.3V logic | 1 |
| Level Shifter | Bidirectional LLC | 5V ↔ 3.3V | 1 |
| AC Input | IEC C14 Receptacle | — | 1 |
| Fuse (AC) | — | 3A Slow Blow | 1 |
| Fuse (Motor) | — | 5A | 1 |
| Polyfuse (Logic) | — | 3A Resettable | 1 |
| Capacitor | C_Polarized | 100µF, decoupling per motor driver | 3 |
| Capacitor | C_Polarized | 470µF, logic rail bulk | 1 |
| Capacitor | C | 0.1µF, decoupling | 7 |

---

### 2. Schematic

[📄 View Full Schematic (PDF)](./electrical/elec_sch.pdf)

The schematic is organized into 4 sheets:

| Sheet | Title | Description |
| :--- | :--- | :--- |
| 1 | System Overview | Top-level hierarchy showing how all sheets interconnect |
| 2 | AC Input & Primary Power | Converts 220V AC mains to regulated 5V and 12V DC rails, with slow-blow fusing and earth protective ground |
| 3 | 12V Motor Power Domain | Three independent DRV8825 motor driver circuits with TVS back-EMF protection and bulk capacitors, driving NEMA17 stepper motors for X, Y, and Z axes |
| 4 | 5V Logic Domain | Raspberry Pi 4 and Arduino Nano V3 connected via bidirectional level shifter, with limit switches and polyfuse protection on the logic rail |

### 3. Calculations

> 📝 **TBD:** Add power budget, current calculations, and signal flow description.

### 4. Electrical Insight

> 📝 **TBD:** Add design decisions — e.g. dual PSU rationale, ground separation strategy, driver protection.

---

## 💻 Software

### 1. Architecture
 
#### 1.1 System Overview
 
The system is split across two processors with clearly separated responsibilities. The Raspberry Pi 4 handles all high-level tasks — running the Flask web server, managing the experiment loop, controlling the camera, and serving the browser-based GUI. The Arduino Nano V3 handles all real-time low-level tasks — generating STEP/DIR pulses for the three stepper motors, polling limit switches, and controlling the shared SLP pin for driver sleep/wake. Communication between the two is via UART serial (currently USB cable, migrating to TX/RX via bidirectional level shifter).
 
![System Overview](https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/software/diagram/System_Overview.jpg)
 
#### 1.2 Software Flow
 
The web GUI runs in any browser on the same network. User actions hit Flask REST endpoints, which dispatch commands to the SerialManager (for motor moves) or CameraManager (for captures). The ExperimentRunner runs as a background thread, orchestrating the full 24/7 scan cycle independently of the GUI.
 
![Software Flow](https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/software/diagram/Software_Flow.jpg)
 
#### 1.3 Experiment Loop
 
Each round begins with an autofocus sweep at the reference well (A1) using the Tenengrad focus metric. The stage then visits every well in serpentine order — move, settle, capture, repeat. After all 96 wells are done, the system waits for the configured interval, then checks whether the experiment end time has been reached. If not, it starts the next round. If yes, the experiment ends automatically.
 
![Experiment Loop](https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/software/diagram/Experiment_Loop.jpg)
 
#### 1.4 Repository Structure
 
```
Automation-Incubator-Microscope/
├── backend/
│   └── app.py              # Flask server — routes, ExperimentRunner, CameraManager, SerialManager
├── frontend/
│   ├── index.html          # Web GUI — stage controls, experiment panel, live status
│   └── assets/
│       └── imbsllogo.png
├── firmware/
│   └── sketch_oct03a.ino   # Arduino Nano V3 — STEP/DIR, SLP, limit switches, stop
├── config.json             # Runtime config — interval, settle delay, storage path, Z range
└── README.md
```
 
---
 
### 2. Firmware
 
The Arduino firmware (`sketch_oct03a.ino`) handles all real-time hardware tasks. It listens for serial commands from the Raspberry Pi and executes them deterministically without OS interference.
 
#### Serial Command Reference
 
| Command | Action |
| :--- | :--- |
| `A1` … `H12` | Move to specified well |
| `home` | Home X and Y axes to limit switches |
| `scan` | Home then serpentine scan all 96 wells |
| `U` | Z axis up one increment |
| `D` | Z axis down one increment |
| `sleep` | Set SLP HIGH — all drivers enter low-power sleep |
| `wake` | Set SLP LOW — all drivers become active |
| `stop` | Abort current movement or scan mid-operation |
 
---
 
### 3. GUI
 
The GUI is a single-page web app served by Flask, accessible from any browser on the same network as the Raspberry Pi. It is built with plain HTML, Tailwind CSS, and vanilla JavaScript — no build step required.
 
**Stage controls** — Home, Z Up, Z Down, Autofocus, Scan All, Stop, Reset Busy are always visible at the top. The 96-well grid below highlights the current well position in real time (polled every 1 second).
 
**Experiment panel** — sits below the grid. User fills in Experiment ID (optional), capture interval, settle delay, storage path, autofocus Z range, and end date/time. Pressing Start saves the settings to `config.json` and launches the experiment loop. A live status box shows round number, total images captured, countdown to next scan, and experiment end time.
 
---
 
### 4. Data Management
 
#### 4.1 Pipeline
 
Every captured image goes through a three-step pipeline immediately after capture: raw array from Picamera2 → BGR conversion → grayscale conversion via OpenCV. Both the raw PNG and grayscale PNG are saved side by side. The original is retained for potential reprocessing.
 
![Data Pipeline](https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/software/diagram/Data_Pipeline.jpg)
 
#### 4.2 Folder Structure
 
```
/data/
└── EXP_001_20260401/
    ├── metadata.json           ← experiment parameters
    ├── A1/
    │   ├── 20260401_080000_A1_r001_raw.png
    │   ├── 20260401_080000_A1_r001_gray.png
    │   └── ...
    ├── A2/
    └── ...
```
 
#### 4.3 File Naming Convention
 
```
YYYYMMDD_HHMMSS_[WellID]_r[Round]_[type].png
```
 
| Field | Example | Description |
| :--- | :--- | :--- |
| YYYYMMDD | 20260401 | Date of capture |
| HHMMSS | 080000 | Time of capture (24h) |
| WellID | A1, B3, H12 | Well position |
| Round | r001, r012 | Scan round index |
| type | raw / gray | Original or grayscale |
 
#### 4.4 Metadata
 
Each experiment generates a `metadata.json` at the experiment root:
 
```json
{
  "experiment_id": "EXP_001_20260401",
  "start_time": "2026-04-01T08:00:00",
  "end_time": "2026-04-08T08:00:00",
  "capture_interval_hours": 2,
  "settle_delay_ms": 500,
  "autofocus_z_range": 20,
  "autofocus_step_size": 1
}
```
 
#### 4.5 Storage Estimate
 
For a 96-well plate, captured every 2 hours over 7 days, saving grayscale PNG (~2 MB each):
 
```
96 wells × 12 captures/day × 7 days = 8,064 images ≈ 16 GB/week
```
 
Recommended storage: USB SSD 256 GB connected to Raspberry Pi.
 
---

### 5. Software Insight

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
