# Automation-Incubator-Microscope

## Mechanical Documentation
This section summarizes the engineering analysis and results for a custom linear stage intended for microscopy applications.

### Kinematic & Motion Analysis
#### Degrees of Freedom (DOF):
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Kinematic%20%26%20Motion%20Analysis.gif" width="800"/>
</p>

- X-axis: 1 translational (stacked system)
- Y-axis: 1 translational
- Z-axis: 1 translational 

All axes exhibited no unintended rotations or free translations, confirming proper constraint and assembly of the stage.

#### Lead Screw Motion:
- Lead screw pitch: 1 mm/rev
- Stepper motor: 200 steps/rev, full-step (x,y,z axis)
- Theoretical linear resolution:

$$
\begin{aligned}
\text{Resolution} &= \frac{\text{Lead Screw Pitch}}{\text{Steps per Revolution}} \\
                  &= \frac{1 \text{mm}}{200 \times 1} \\
                  &= 0.005 \text{mm} \\
                  &= 5 \mu\text{m}
\end{aligned}
$$

- Distance between plates = 9 mm
- Theoretical required number of motor pulses:

$$
\begin{aligned}
\text{Required Steps}
&= \frac{\text{Travel Distance}}{\text{Resolution}} \\
&= \frac{9 \text{mm}}{5 \mu\text{m}} \\
&= \frac{9000 \mu\text{m}}{5 \mu\text{m}} \\
&= 1800 \text{steps}
\end{aligned}
$$

#### Interference Analysis:
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Inference%20Analysis.jpeg" width="800"/>
</p>

<p align="justify">
The interference analysis reports several interferences; however, these are not physically relevant in real-world assembly. The detected interferences occur within precision components such as linear rails and threaded regions of the KFL08 bearing, which are intentionally modeled with overlapping geometry in CAD. Therefore, no actual collisions or functional interferences are present in the final design.
</p>

### Structural Rigidity
#### Stage Plate Analysis (Static Load):
- Load applied: Gravity force only
- Gravity direction: Vertical (−Z axis)
- Acceleration: 9.81 m/s²

##### A. PLA-CF Configuration
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/PLA-CF_1.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/PLA-CF_02.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/PLA-CF_3.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/PLA-CF_4.png" width="500" height="400" />
</p>

- The displacement contour shows dominant green regions on the structure.
- These green regions correspond to a displacement range of approximately 0.0349 – 0.05235 mm.
- The deformation is mainly concentrated around:
  - The upper stage plate
  - The area near the stepper motor mounting
- This indicates that the self-weight of the stepper motor is the dominant contributor to the overall deformation.
- Due to the lower elastic modulus of PLA-CF, the structure exhibits global sagging under gravity-only loading.

##### B. Aluminum 6061
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Alumnium_2.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Aluminum_1.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Aluminum_3.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Aluminum_4.png" width="500" height="400" />
</p>

- The displacement contour is dominated by dark blue regions.
- Dark blue corresponds to near-zero displacement (≈ 0 mm, minimum value).
- This indicates that the structure experiences negligible deformation under gravity-only loading.
- The higher stiffness of Aluminum 6061 effectively resists bending caused by the self-weight of the system, including the stepper motor.

##### Summary of Stage Plate Analysis
| Parameter | PLA-CF | Aluminum 6061 |
|------------|------------|----------------|
| Stiffness | Moderate | Very High |
| Max Deflection | ~54 µm | <1 µm |
| Structural Rigidity | Exhibits global sagging | Negligible bending |
| Focus Reliability | Not suitable for high magnification | Suitable for precision imaging |
| Engineering Verdict | Acceptable for non-critical parts | Recommended for structural components |

#### Motor Bracket Analysis:
Still in progress (sip)

### Thermal Consideration
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20X.jpeg" width="200" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20Y.jpeg" width="200" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20Z.jpeg" width="200" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Wellplate.jpeg" width="200" />
</p>


### Vibration Consideration
sip

### Drawing & Tolerance
sip

### Tolerance Stack Analysis
sip

## Electrical Documentation
### System Architecture
#### A. Power Distribution Architecture
```mermaid
flowchart TD
    A[PSU 12V 8.5A] --> B[Fuse 8A]
    B --> C[Elco]
    C --> |12V 1.2A| D1[Driver X]
    C --> |12V 1.2A| D2[Driver Y]
    C --> |12V 1.2A| D3[Driver Z]
    C --> |12V| D4[Buck Converter 5V]
    D4 --> |5V 3A| E1[Raspberry Pi 4 Model B]
    D4 --> |5V 0.2A| E2[Arduino Nano]
```
