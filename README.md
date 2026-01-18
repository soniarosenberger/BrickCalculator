# BrickCalculator
## Brick Lining Template Generator

This project is designed for hands-on builders who want accurate layout geometry without needing CAD software. It provides visual templates and numeric outputs that can be taken directly into the shop for cutting and layout.

## What This Tool Does

The script calculates wedge brick geometry for building a segmented circular lining and produces:

### Full Ring Layout (Top View)

- Shows the complete N-sided ring layout  
- Displays barrel inside diameter  
- Displays inner clearance across flats and corners  
- Shows exact brick placement around the circle  
- Helps visualize fit before cutting material  

### Single Brick Cut Template

- Shows a flat trapezoidal brick template  
- Displays:  
  - Outer face length  
  - Inner face length  
  - Brick thickness  
  - Taper per side  
  - Miter angle per cut  
- Includes engineering-style dimension lines and angle callouts  
- Can be used as a direct cutting reference  

### Terminal Output

The program also prints all calculated geometry values to the terminal so you can copy numbers directly into a notebook or shop notes.

## Who This Is For

This tool is useful for:

- DIY furnace builders  
- Kiln builders  
- Pizza oven and firebox projects  
- Refractory lining fabrication  
- Segmented circular masonry builds  
- Makers working without CAD  

If you are cutting straight bricks to form a circular ring, this script removes guesswork and trial fitting.

## Requirements

- Python 3.x  
- matplotlib  

Install dependency:

    pip install matplotlib

## How To Use

1. Open the script file.

2. Edit the input values at the bottom:

    BARREL_DIAMETER_IN = 24  
    BRICK_THICKNESS_IN = 4.5  
    N = 8  
    BRICK_OUTER_FACE_IN = 9.0  
    SAW_KERF_IN = 0.125  

### Parameter Descriptions

- **BARREL_DIAMETER_IN**  
  Inside diameter of the barrel or shell you are lining.

- **BRICK_THICKNESS_IN**  
  Radial thickness of the lining (brick depth inward).

- **N**  
  Number of bricks used to form one full ring.

- **BRICK_OUTER_FACE_IN**  
  Length of the outer brick face (the side touching the barrel wall).

- **SAW_KERF_IN**  
  Blade width (displayed for reference, does not affect geometry).

3. Run the script:

    python draw_template.py

4. A window will open showing:

- Ring layout (left)  
- Brick cut template (right)  

5. Use the printed output and visual template to guide cutting and assembly.

## Output Units

- All values are in **inches**  
- Angles are shown in **degrees**  
- Geometry is calculated assuming ideal straight cuts  

## Important Notes

- This tool assumes:  
  - Straight miter cuts  
  - Uniform brick thickness  
  - Perfectly circular barrel interior  
- Saw kerf is displayed for planning purposes only and does not modify calculations.  
- Always dry-fit bricks before final installation.  

## Why This Exists

Building circular linings from straight bricks normally requires trial cuts, repeated test fitting, or CAD work. This tool provides:

- Fast iteration  
- Visual feedback  
- Shop-ready measurements  
- Minimal setup  
