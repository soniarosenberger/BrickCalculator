# Refractory Brick Lining Template Generator

## Overview
This Python script generates a refractory brick lining template for a barrel. The script produces two outputs:
1. A top-view full ring layout with key diameters.
2. A single-brick cut template with dimensions and miter angle callouts.

Additionally, the script prints the computed geometry to the terminal for reference.

## Features
- Generates a top-view diagram of the brick lining.
- Creates a single-brick cut template with precise dimensions and angles.
- Provides detailed terminal output of the input parameters and calculated results.
- Includes validation for input parameters to ensure accurate results.

## Requirements
- Python 3.6 or higher
- Matplotlib library

## Installation
1. Ensure you have Python 3.6 or higher installed on your system.
2. Install the required Python library:
   ```bash
   pip install matplotlib
   ```

## Usage
1. Clone this repository or download the script `brickcalculator.py`.
2. Open a terminal and navigate to the directory containing the script.
3. Run the script using the following command:
   ```bash
   python3 brickcalculator.py
   ```
4. Follow the prompts to input the required dimensions:
   - Barrel inside diameter (in)
   - Barrel wall thickness (in)
   - Minimum backup insulation thickness (in)
   - Brick thickness (radial, in)
   - Number of bricks per ring (N)
   - Maximum brick outer face length (in)
   - Saw kerf / blade width (in)

5. The script will generate the diagrams and display the computed geometry in the terminal.

## Input Parameters
- **Barrel inside diameter (in)**: The inner diameter of the barrel.
- **Barrel wall thickness (in)**: The thickness of the barrel wall.
- **Minimum backup insulation thickness (in)**: The minimum thickness of the backup insulation layer.
- **Brick thickness (radial, in)**: The radial thickness of each brick.
- **Number of bricks per ring (N)**: The number of bricks in a single ring. Must be 3 or greater.
- **Maximum brick outer face length (in)**: The maximum length of the outer face of each brick.
- **Saw kerf / blade width (in)**: The width of the saw blade used for cutting bricks (informational).

## Output
### Diagrams
1. **Top-View Diagram**:
   - Displays the full ring layout of the brick lining.
   - Includes key diameters and dimensions.
   - Shows the backup insulation layer (yellow shaded) and barrel wall.

2. **Single-Brick Cut Template**:
   - Provides a detailed cut template for a single brick.
   - Includes dimensions for the outer face, inner face, thickness, and taper.
   - Displays miter angles for precise cutting.

### Terminal Output
The script prints the following information to the terminal:
- Input parameters.
- Calculated values, including:
  - Central angle (°)
  - Miter angle per end (°)
  - Inner face length (in)
  - Taper per side (in)
  - Inner diameter across flats (in)
  - Inner diameter across corners (in)
  - Brick ring outer diameter (max, in)
  - Barrel outer diameter (in)
  - Maximum gap thickness (in) (between backup insulation layer annulus and outer brick flats)

## Example
The following example shows inputs and outputs for lining a 55-gallon steel barrel with a backup insulation layer of minimum radial thickness 3.5", and a 6-sided refractory brick hot-face lining. K-23 brick dimesions (9"x4.5"x2.5") are used in this example. Plot output can be viewed at 6_sided.png.

### Input:
```
Barrel inside diameter (in): 22.9
Barrel wall thickness (in): 0.05
Minimum backup insulation thickness (in): 3.5
Brick thickness (radial, in): 2.5
Number of bricks per ring (N): 6
Maximum brick outer face length (in): 9
Saw kerf / blade width (in): 0.125
```

### Output:
#### Terminal:
```
=== INPUTS ===
N:                               6
Barrel inside diameter:          22.900 in
Barrel wall thickness:           0.050 in
Backup insulation min thickness: 3.500 in
Brick thickness (radial):        2.500 in
Brick outer face length:         9.000 in
Saw kerf:                        0.125 in

=== OUTPUTS ===
Central angle:                   60.000°
Miter angle per end:             30.000° (off-square)
Inner face length:               5.063 in
Taper per side:                  1.443 in
Inner diameter across flats:     9.440 in
Inner diameter across corners:   10.900 in
Brick ring outer diameter (max): 15.900 in
Barrel outer diameter:           23.000 in
Max gap thickness:               1.065 in
```

#### Diagrams:
- A top-view diagram of the brick lining.
- A single-brick cut template with dimensions and miter angles.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Author
Sonia Rosenberger
