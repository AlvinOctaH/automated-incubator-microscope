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

##### A. PLA-CF
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
- Dark blue corresponds to near-zero displacement (<1 µm, minimum value).
- This indicates that the structure experiences negligible deformation under gravity-only loading.
- The higher stiffness of Aluminum 6061 effectively resists bending caused by the self-weight of the system, including the stepper motor.

##### Summary of Stage Plate Analysis
<div align="center">


| Parameter | PLA-CF | Aluminum 6061 |
| :--- | :--- | :--- |
| Stiffness | Moderate | Very High |
| Max Deflection | ~54 µm | <1 µm |
| Structural Rigidity | Exhibits global sagging | Negligible bending |
| Focus Reliability | Not suitable for high magnification | Suitable for precision imaging |
| Engineering Verdict | Acceptable for non-critical parts | Recommended for structural components |

</div>


#### Motor Bracket Analysis:
##### A. X Motor Bracket
###### Previous Version
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx0.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx0_2.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx0_3.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx0_4.png" width="500" height="400" />
</p>

###### New Version
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx1.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx1_2.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx1_3.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketx1_4.png" width="500" height="400" />
</p>

##### B. Y Motor Bracket
###### Previous Version
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety0.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety0_2.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety0_3.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety0_4.png" width="500" height="400" />
</p>

###### New Version
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety1.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety1_2.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety1_3.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/brackety1_4.png" width="500" height="400" />
</p>

##### C. Z Motor Bracket
###### Previous Version
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz0.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz0_2.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz0_3.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz0_4.png" width="500" height="400" />
</p>

###### New Version
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz1.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz1_2.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz1_3.png" width="500" height="400" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/bracketz1_4.png" width="500" height="400" />
</p>

##### Summary of Motor Bracket Analysis
<div align="center">

</div>

### Vibration Consideration
sip

### Thermal Consideration
<p align="center">
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20X.jpeg" width="200" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20Y.jpeg" width="200" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Step%20Motor%20Z.jpeg" width="200" />
  <img src="https://github.com/AlvinOctaH/Automation-Incubator-Microscope/blob/main/src/Wellplate.jpeg" width="200" />
</p>

### Drawing & Tolerance
sip

## Electrical Documentation
### System Architecture
#### Theoritical Approach
Fuse sizing rule


#### Power Distribution Architecture
```mermaid
flowchart TD
    A[IEC C13 to Type B] --> B[IEC C14 EMI suppression 10A 125/250VAC]
    B --> C1[Mean Well LRS-100-12 12V 8.5A]
    B --> C2[Mean Well RS-25-5 5V 5A]
    C1 --> D1[Fuse 5A Slow Blow]
    C2 --> D2[Fuse 5A Fast Blow]
    D1 --> |12V 1.2A| E1[Driver X]
    D1 --> |12V 1.2A| E2[Driver Y]
    D1 --> |12V 1.2A| E3[Driver Z]
    D2 --> |5V 3A| E4[Raspberry Pi 4 Model B]
    D2 --> |5V 0.2A| E5[Arduino Nano]
```
