# brickcalculator.py
# Author: Sonia Rosenberger
# Date: February 12th, 2026
# Purpose: Draw a template for an N-sided refractory brick lining inside a barrel:
#          (1) a top-view full ring layout with key diameters and (2) a single-brick cut template
#          with dimensions and miter angle callouts. Prints computed geometry to the terminal.
# Usage: Run as a script. You will be prompted to enter values one at a time.

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Arc, Wedge


# ==================== CONSTANTS ====================

# Plotting configuration
FIGURE_WIDTH = 13.8
FIGURE_HEIGHT = 6.3
PLOT_MARGIN = 2.2
TABLE_ROW_GAP = 1.2
TABLE_Y_OFFSET = 0.5

# Insulation visualization
INSULATION_COLOR = "#FFE680"  # light yellow
INSULATION_ALPHA = 0.6

# Brick template layout
MITER_REFERENCE_ANGLE_DEG = 270.0  # vertical downward reference
BRICK_TITLE_OFFSET_Y = 4.15
BRICK_INFO_OFFSET_Y = 2.05
ARC_LABEL_RADIUS_MULTIPLIER = 1.25

# Dimension offsets and sizes
MITER_ARC_RADIUS = 0.9
MITER_REF_LINE_LENGTH = 1.4
MITER_LABEL_FONT_SIZE = 8


# ==================== HELPER FUNCTIONS ====================

def dim(ax, p1, p2, offset=(0, 0), text="", text_offset=(0, 0), lw=1):
    """Engineering-style dimension with extension lines and <-> arrows."""
    offset_x, offset_y = offset
    q1 = (p1[0] + offset_x, p1[1] + offset_y)
    q2 = (p2[0] + offset_x, p2[1] + offset_y)

    ax.plot([p1[0], q1[0]], [p1[1], q1[1]], lw=lw, color='black')
    ax.plot([p2[0], q2[0]], [p2[1], q2[1]], lw=lw, color='black')

    ax.annotate(
        "",
        xy=q2, xytext=q1,
        arrowprops=dict(arrowstyle="<->", lw=lw, shrinkA=0, shrinkB=0, color='black')
    )

    text_x = (q1[0] + q2[0]) / 2 + text_offset[0]
    text_y = (q1[1] + q2[1]) / 2 + text_offset[1]
    ax.text(text_x, text_y, text, fontsize=10, ha="center", va="center")


def angle_arc(ax, center, start_deg, end_deg, radius, label, label_angle=None, lw=1):
    """Arc + label for an angle callout."""
    arc = Arc(center, 2 * radius, 2 * radius, theta1=start_deg, theta2=end_deg, lw=lw, color='black')
    ax.add_patch(arc)

    if label_angle is None:
        label_angle = (start_deg + end_deg) / 2

    label_x = center[0] + ARC_LABEL_RADIUS_MULTIPLIER * radius * math.cos(math.radians(label_angle))
    label_y = center[1] + ARC_LABEL_RADIUS_MULTIPLIER * radius * math.sin(math.radians(label_angle))
    ax.text(label_x, label_y, label, fontsize=10, ha="center", va="center")


def plot_circle(ax, radius, lw=1, color='black'):
    """Plot a circle of a given radius using 0..360 degree sampling."""
    angles_deg = range(361)
    xs = [radius * math.cos(math.radians(deg)) for deg in angles_deg]
    ys = [radius * math.sin(math.radians(deg)) for deg in angles_deg]
    ax.plot(xs, ys, lw=lw, color=color)


def draw_wedge_bricks(ax, inner_radius, outer_radius, num_bricks):
    """Draw N wedge bricks between inner_radius and outer_radius as 4-pt polygons."""
    delta_theta_rad = 2 * math.pi / num_bricks
    for i in range(num_bricks):
        theta0 = i * delta_theta_rad
        theta1 = (i + 1) * delta_theta_rad
        inner_pt0 = (inner_radius * math.cos(theta0), inner_radius * math.sin(theta0))
        inner_pt1 = (inner_radius * math.cos(theta1), inner_radius * math.sin(theta1))
        outer_pt1 = (outer_radius * math.cos(theta1), outer_radius * math.sin(theta1))
        outer_pt0 = (outer_radius * math.cos(theta0), outer_radius * math.sin(theta0))
        ax.add_patch(Polygon([inner_pt0, inner_pt1, outer_pt1, outer_pt0], closed=True, fill=False, lw=1))


def draw_miter_callout(ax, corner_pt, arc_start_deg, arc_end_deg, label_text, label_angle_deg, lw=1):
    """Draw dashed vertical reference line and an angle arc/label for a miter callout."""
    # Dashed vertical reference line
    ax.plot(
        [corner_pt[0], corner_pt[0]],
        [corner_pt[1], corner_pt[1] - MITER_REF_LINE_LENGTH],
        linestyle="--",
        linewidth=1,
        color='black'
    )

    angle_arc(
        ax, corner_pt,
        start_deg=arc_start_deg,
        end_deg=arc_end_deg,
        radius=MITER_ARC_RADIUS,
        label=label_text,
        label_angle=label_angle_deg,
        lw=lw
    )


def tweak_last_two_angle_labels(ax, right_dx_dy, left_dx_dy):
    """Shrink font and nudge left/right angle labels (assumes last two texts are angle labels)."""
    for txt in ax.texts[-2:]:
        txt.set_fontsize(MITER_LABEL_FONT_SIZE)

    right_label = ax.texts[-1]
    rx, ry = right_label.get_position()
    right_label.set_position((rx + right_dx_dy[0], ry + right_dx_dy[1]))

    left_label = ax.texts[-2]
    lx, ly = left_label.get_position()
    left_label.set_position((lx + left_dx_dy[0], ly + left_dx_dy[1]))


# ==================== VALIDATION ====================

def validate_inputs(barrel_diameter_in, brick_thickness_in, num_bricks,
                    desired_brick_face_in, saw_kerf_in, barrel_wall_thickness_in,
                    insulation_thickness_in):
    """
    Validate all input parameters.

    Raises:
        ValueError: If any input parameter is invalid
    """
    if num_bricks < 3:
        raise ValueError("Number of bricks must be >= 3.")
    if barrel_diameter_in <= 0:
        raise ValueError("Barrel inside diameter must be > 0.")
    if brick_thickness_in <= 0:
        raise ValueError("Brick thickness must be > 0.")
    if desired_brick_face_in <= 0:
        raise ValueError("Brick outer face length must be > 0.")
    if saw_kerf_in < 0:
        raise ValueError("Saw kerf must be >= 0.")
    if barrel_wall_thickness_in < 0:
        raise ValueError("Barrel wall thickness must be >= 0.")
    if insulation_thickness_in < 0:
        raise ValueError("Backup insulation thickness must be >= 0.")


# ==================== GEOMETRY CALCULATIONS ====================

def calculate_brick_geometry(barrel_diameter_in, brick_thickness_in, num_bricks,
                            desired_brick_face_in, barrel_wall_thickness_in,
                            insulation_thickness_in):
    """
    Calculate all geometric dimensions for the brick ring.

    Args:
        barrel_diameter_in: Inside diameter of barrel (inches)
        brick_thickness_in: Radial brick thickness (inches)
        num_bricks: Number of bricks per ring
        desired_brick_face_in: Desired outer face length of brick (inches)
        barrel_wall_thickness_in: Thickness of barrel wall (inches)
        insulation_thickness_in: Thickness of backup insulation (inches)

    Returns:
        Dictionary containing all calculated geometric values
    """
    # Basic barrel geometry
    barrel_inner_radius_in = barrel_diameter_in / 2.0
    barrel_outer_diameter_in = barrel_diameter_in + 2.0 * barrel_wall_thickness_in
    barrel_outer_radius_in = barrel_outer_diameter_in / 2.0

    # Insulation layer (fixed thickness)
    insulation_inner_radius_in = barrel_inner_radius_in - insulation_thickness_in
    if insulation_inner_radius_in <= 0:
        raise ValueError("Insulation thickness is too large for the barrel inner diameter.")

    # Angle calculations
    central_angle_deg = 360.0 / num_bricks
    miter_angle_deg = 180.0 / num_bricks  # off-square per end
    miter_angle_rad = math.radians(miter_angle_deg)

    # Determine actual brick size (may be reduced to fit)
    desired_brick_outer_radius_in = desired_brick_face_in / (2.0 * math.sin(math.pi / num_bricks))

    if desired_brick_outer_radius_in > insulation_inner_radius_in:
        # Brick too large - use maximum size that fits
        brick_outer_radius_in = insulation_inner_radius_in
        brick_face_in = 2.0 * brick_outer_radius_in * math.sin(math.pi / num_bricks)
        size_adjusted = True
    else:
        # Desired size fits
        brick_outer_radius_in = desired_brick_outer_radius_in
        brick_face_in = desired_brick_face_in
        size_adjusted = False

    # Brick inner boundary
    brick_inner_radius_in = brick_outer_radius_in - brick_thickness_in
    if brick_inner_radius_in <= 0:
        raise ValueError("Brick thickness is too large for the brick ring radius.")

    brick_ring_outer_diameter_in = 2.0 * brick_outer_radius_in

    # Inner face length (trapezoid geometry)
    inner_face_in = brick_face_in - 2.0 * brick_thickness_in * math.tan(miter_angle_rad)
    if inner_face_in <= 0:
        raise ValueError("Inner face computed <= 0. With these inputs, this wedge is not possible.")

    taper_per_side_in = (brick_face_in - inner_face_in) / 2.0

    # Clear opening dimensions (N-sided polygon formed by inner faces)
    clear_opening_apothem_in = inner_face_in / (2.0 * math.tan(math.pi / num_bricks))
    clear_opening_circumradius_in = inner_face_in / (2.0 * math.sin(math.pi / num_bricks))
    clear_diameter_across_flats_in = 2.0 * clear_opening_apothem_in
    clear_diameter_across_corners_in = 2.0 * clear_opening_circumradius_in

    # Gap between brick outer polygon and insulation inner circle
    brick_polygon_apothem_in = brick_outer_radius_in * math.cos(math.pi / num_bricks)
    gap_max_in = insulation_inner_radius_in - brick_polygon_apothem_in  # at face centers
    gap_min_in = insulation_inner_radius_in - brick_outer_radius_in     # at vertices

    return {
        'barrel_inner_radius_in': barrel_inner_radius_in,
        'barrel_outer_diameter_in': barrel_outer_diameter_in,
        'barrel_outer_radius_in': barrel_outer_radius_in,
        'insulation_inner_radius_in': insulation_inner_radius_in,
        'central_angle_deg': central_angle_deg,
        'miter_angle_deg': miter_angle_deg,
        'miter_angle_rad': miter_angle_rad,
        'brick_outer_radius_in': brick_outer_radius_in,
        'brick_inner_radius_in': brick_inner_radius_in,
        'brick_ring_outer_diameter_in': brick_ring_outer_diameter_in,
        'brick_face_in': brick_face_in,
        'inner_face_in': inner_face_in,
        'taper_per_side_in': taper_per_side_in,
        'clear_opening_apothem_in': clear_opening_apothem_in,
        'clear_opening_circumradius_in': clear_opening_circumradius_in,
        'clear_diameter_across_flats_in': clear_diameter_across_flats_in,
        'clear_diameter_across_corners_in': clear_diameter_across_corners_in,
        'brick_polygon_apothem_in': brick_polygon_apothem_in,
        'gap_max_in': gap_max_in,
        'gap_min_in': gap_min_in,
        'size_adjusted': size_adjusted
    }


# ==================== PLOTTING FUNCTIONS ====================

def plot_ring_view(ax, inputs, calcs):
    """
    Plot the top-view ring layout showing barrel, insulation, and brick ring.

    Args:
        ax: Matplotlib axis
        inputs: Dictionary of input parameters
        calcs: Dictionary of calculated values
    """
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    ax.set_title("Top View", fontsize=12)

    # Draw concentric circles (each with different color for visibility)
    plot_circle(ax, calcs['barrel_inner_radius_in'], lw=1, color='blue')
    plot_circle(ax, calcs['barrel_outer_radius_in'], lw=1, color='navy')
    plot_circle(ax, calcs['brick_outer_radius_in'], lw=1, color='red')
    plot_circle(ax, calcs['brick_inner_radius_in'], lw=1, color='orange')
    # Circle that touches the inner brick faces (flats)
    inner_flats_circle_radius = calcs['brick_inner_radius_in'] * math.cos(math.pi / inputs['num_bricks'])
    plot_circle(ax, inner_flats_circle_radius, lw=1, color='green')

    # Draw insulation annulus (shaded)
    insulation_annulus = Wedge(
        center=(0, 0),
        r=calcs['barrel_inner_radius_in'],
        theta1=0,
        theta2=360,
        width=inputs['insulation_thickness_in'],
        color=INSULATION_COLOR,
        alpha=INSULATION_ALPHA
    )
    ax.add_patch(insulation_annulus)

    # Draw insulation inner boundary (dashed)
    angles_deg = range(361)
    xs = [calcs['insulation_inner_radius_in'] * math.cos(math.radians(deg)) for deg in angles_deg]
    ys = [calcs['insulation_inner_radius_in'] * math.sin(math.radians(deg)) for deg in angles_deg]
    ax.plot(xs, ys, lw=1, linestyle='--', color='black')

    # Draw wedge bricks
    draw_wedge_bricks(ax, calcs['brick_inner_radius_in'], calcs['brick_outer_radius_in'], inputs['num_bricks'])

    # Add text table below diagram
    plot_limit = max(calcs['barrel_outer_radius_in'], calcs['barrel_inner_radius_in']) + PLOT_MARGIN

    table_x = 0.0
    table_y_start = -(plot_limit + TABLE_Y_OFFSET)

    diameter_rows = [
        ("Barrel inside diameter", f"Ø {inputs['barrel_diameter_in']:.3f} in"),
        ("Barrel outer diameter", f"Ø {calcs['barrel_outer_diameter_in']:.3f} in"),
        ("Brick ring outer diameter", f"Ø {calcs['brick_ring_outer_diameter_in']:.3f} in"),
        ("Inner diameter across flats", f"Ø {calcs['clear_diameter_across_flats_in']:.3f} in"),
        ("Inner diameter across corners", f"Ø {calcs['clear_diameter_across_corners_in']:.3f} in"),
    ]

    thickness_rows = [
        ("Backup insulation thickness", f"{inputs['insulation_thickness_in']:.3f} in"),
        ("Barrel wall thickness", f"{inputs['barrel_wall_thickness_in']:.3f} in"),
        ("Gap at brick face centers (max)", f"{calcs['gap_max_in']:.3f} in"),
        ("Gap at brick vertices (min)", f"{calcs['gap_min_in']:.3f} in"),
    ]

    all_rows = diameter_rows + thickness_rows

    for i, (desc, val) in enumerate(all_rows):
        ax.text(
            table_x, table_y_start - i * TABLE_ROW_GAP,
            f"{desc}: {val}",
            fontsize=10, ha="center", va="center"
        )

    ax.set_xlim(-plot_limit, plot_limit)
    ax.set_ylim(-(plot_limit + 8.0), plot_limit)


def plot_brick_template(ax, inputs, calcs):
    """
    Plot the single brick cut template with dimensions and miter angles.

    Args:
        ax: Matplotlib axis
        inputs: Dictionary of input parameters
        calcs: Dictionary of calculated values
    """
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    brick_face_in = calcs['brick_face_in']
    brick_thickness_in = inputs['brick_thickness_in']
    inner_face_in = calcs['inner_face_in']
    taper_per_side_in = calcs['taper_per_side_in']
    miter_angle_deg = calcs['miter_angle_deg']

    # Title
    brick_center_x = brick_face_in / 2.0
    title_y = brick_thickness_in + BRICK_TITLE_OFFSET_Y

    ax.text(
        brick_center_x,
        title_y,
        "Single Brick - CUT TEMPLATE",
        fontsize=12,
        ha="center",
        va="bottom",
        transform=ax.transData
    )

    # Draw trapezoid (outer face at top, inner face at bottom)
    outer_left_pt = (0.0, brick_thickness_in)
    outer_right_pt = (brick_face_in, brick_thickness_in)
    inner_right_pt = (taper_per_side_in + inner_face_in, 0.0)
    inner_left_pt = (taper_per_side_in, 0.0)

    ax.add_patch(
        Polygon([outer_left_pt, outer_right_pt, inner_right_pt, inner_left_pt],
                closed=True, fill=False, lw=2)
    )

    # Add dimension annotations
    dim(ax, outer_left_pt, outer_right_pt,
        offset=(0, 0.9),
        text=f"{brick_face_in:.3f} in  (Outer face)",
        text_offset=(0, 0.25))

    dim(ax, inner_left_pt, inner_right_pt,
        offset=(0, -0.9),
        text=f"{inner_face_in:.3f} in  (Inner face)",
        text_offset=(0, -0.25))

    dim(ax, (brick_face_in, 0.0), (brick_face_in, brick_thickness_in),
        offset=(1.3, 0),
        text=f"{brick_thickness_in:.3f} in  (Thickness)",
        text_offset=(0.25, -1))

    dim(ax, (0.0, 0.0), (taper_per_side_in, 0.0),
        offset=(0, -1.6),
        text=f"{taper_per_side_in:.3f} in  (Taper each side)",
        text_offset=(0, -0.25))

    # Miter angle callouts
    left_cut_angle_deg = MITER_REFERENCE_ANGLE_DEG + miter_angle_deg
    right_cut_angle_deg = MITER_REFERENCE_ANGLE_DEG - miter_angle_deg

    # Left miter callout
    draw_miter_callout(
        ax=ax,
        corner_pt=outer_left_pt,
        arc_start_deg=MITER_REFERENCE_ANGLE_DEG,
        arc_end_deg=left_cut_angle_deg,
        label_text=f"{miter_angle_deg:.2f}°",
        label_angle_deg=MITER_REFERENCE_ANGLE_DEG + miter_angle_deg / 2.0,
        lw=1
    )

    # Right miter callout
    draw_miter_callout(
        ax=ax,
        corner_pt=outer_right_pt,
        arc_start_deg=right_cut_angle_deg,
        arc_end_deg=MITER_REFERENCE_ANGLE_DEG,
        label_text=f"{miter_angle_deg:.2f}°",
        label_angle_deg=MITER_REFERENCE_ANGLE_DEG - miter_angle_deg / 2.0,
        lw=1
    )

    # Adjust miter label positions
    tweak_last_two_angle_labels(ax, right_dx_dy=(0.50, -0.05), left_dx_dy=(-0.50, -0.05))

    # Add info text
    ax.text(
        brick_face_in / 2.0,
        brick_thickness_in + BRICK_INFO_OFFSET_Y,
        f"Miter per end = {miter_angle_deg:.2f}° (off-square)\n"
        f"Central angle = {calcs['central_angle_deg']:.2f}°\n"
        f"Saw kerf = {inputs['saw_kerf_in']:.3f} in",
        fontsize=9.7, ha="center", va="center"
    )

    ax.set_xlim(-2.0, brick_face_in + 5.5)
    ax.set_ylim(-3.0, brick_thickness_in + 3.0)


# ==================== OUTPUT FUNCTIONS ====================

def print_results(inputs, calcs):
    """
    Print all input parameters and calculated results to terminal.

    Args:
        inputs: Dictionary of input parameters
        calcs: Dictionary of calculated values
    """
    print("\n=== INPUTS ===")
    print(f"N:                               {inputs['num_bricks']}")
    print(f"Barrel inside diameter:          {inputs['barrel_diameter_in']:.3f} in")
    print(f"Barrel wall thickness:           {inputs['barrel_wall_thickness_in']:.3f} in")
    print(f"Backup insulation thickness:     {inputs['insulation_thickness_in']:.3f} in")
    print(f"Brick thickness (radial):        {inputs['brick_thickness_in']:.3f} in")
    print(f"Desired brick outer face length: {inputs['desired_brick_face_in']:.3f} in")
    print(f"Saw kerf:                        {inputs['saw_kerf_in']:.3f} in")

    if calcs['size_adjusted']:
        print(f"\n*** BRICK SIZE ADJUSTED TO FIT ***")
        print(f"Desired face length ({inputs['desired_brick_face_in']:.3f} in) was too large.")
        print(f"Using maximum face length that fits: {calcs['brick_face_in']:.3f} in")

    print("\n=== OUTPUTS ===")
    print(f"Brick outer face length (actual): {calcs['brick_face_in']:.3f} in")
    print(f"Central angle:                   {calcs['central_angle_deg']:.3f}°")
    print(f"Miter angle per end:             {calcs['miter_angle_deg']:.3f}° (off-square)")
    print(f"Brick ring outer radius:         {calcs['brick_outer_radius_in']:.3f} in")
    print(f"Brick ring outer diameter:       {calcs['brick_ring_outer_diameter_in']:.3f} in")
    print(f"Insulation inner radius:         {calcs['insulation_inner_radius_in']:.3f} in")
    print(f"Inner face length:               {calcs['inner_face_in']:.3f} in")
    print(f"Taper per side:                  {calcs['taper_per_side_in']:.3f} in")
    print(f"Inner diameter across flats:     {calcs['clear_diameter_across_flats_in']:.3f} in")
    print(f"Inner diameter across corners:   {calcs['clear_diameter_across_corners_in']:.3f} in")
    print(f"Barrel outer diameter:           {calcs['barrel_outer_diameter_in']:.3f} in")
    print(f"Gap at brick face centers (max): {calcs['gap_max_in']:.3f} in")
    print(f"Gap at brick vertices (min):     {calcs['gap_min_in']:.3f} in")


# ==================== MAIN FUNCTION ====================

def generate_brick_template(barrel_diameter_in, brick_thickness_in, num_bricks,
                           desired_brick_face_in, saw_kerf_in, barrel_wall_thickness_in,
                           insulation_thickness_in):
    """
    Generate refractory brick lining template with diagrams and dimensions.

    Creates two diagrams:
    1. Top view of the full brick ring layout
    2. Single brick cut template with dimensions and miter angles

    Args:
        barrel_diameter_in: Inside diameter of barrel (inches)
        brick_thickness_in: Radial brick thickness (inches)
        num_bricks: Number of bricks per ring
        desired_brick_face_in: Desired outer face length of brick (inches)
        saw_kerf_in: Blade width (inches) - informational only
        barrel_wall_thickness_in: Thickness of barrel wall (inches) - diagram only
        insulation_thickness_in: Thickness of backup insulation (inches)

    Raises:
        ValueError: If inputs are invalid or geometry is impossible
    """
    # Validate inputs
    validate_inputs(barrel_diameter_in, brick_thickness_in, num_bricks,
                   desired_brick_face_in, saw_kerf_in, barrel_wall_thickness_in,
                   insulation_thickness_in)

    # Build input dictionary for passing to other functions
    inputs = {
        'barrel_diameter_in': barrel_diameter_in,
        'brick_thickness_in': brick_thickness_in,
        'num_bricks': num_bricks,
        'desired_brick_face_in': desired_brick_face_in,
        'saw_kerf_in': saw_kerf_in,
        'barrel_wall_thickness_in': barrel_wall_thickness_in,
        'insulation_thickness_in': insulation_thickness_in
    }

    # Calculate all geometry
    calcs = calculate_brick_geometry(
        barrel_diameter_in, brick_thickness_in, num_bricks,
        desired_brick_face_in, barrel_wall_thickness_in, insulation_thickness_in
    )

    # Create figure with two subplots
    fig, (ax_ring, ax_brick) = plt.subplots(1, 2, figsize=(FIGURE_WIDTH, FIGURE_HEIGHT))
    fig.suptitle(f"Template for {num_bricks}-Sided Brick Lining", fontsize=14)

    # Plot diagrams
    plot_ring_view(ax_ring, inputs, calcs)
    plot_brick_template(ax_brick, inputs, calcs)

    # Print results to terminal
    print_results(inputs, calcs)

    # Display
    plt.tight_layout()
    plt.show()


# ==================== INTERACTIVE ENTRY ====================

if __name__ == "__main__":

    def prompt_float(prompt_text):
        """Prompt for a floating point value with validation."""
        while True:
            user_input = input(prompt_text).strip()
            try:
                return float(user_input)
            except ValueError:
                print("  Invalid input. Please enter a numeric value.")

    def prompt_int(prompt_text):
        """Prompt for an integer value with validation."""
        while True:
            user_input = input(prompt_text).strip()
            try:
                return int(user_input)
            except ValueError:
                print("  Invalid input. Please enter an integer value.")

    print("\nRefractory Brick Lining Template Generator")
    print("Enter all dimensions in inches.\n")

    barrel_diameter = prompt_float("Barrel inside diameter (in): ")
    barrel_wall = prompt_float("Barrel wall thickness (in): ")
    insulation = prompt_float("Backup insulation thickness (in): ")
    brick_thickness = prompt_float("Brick thickness (radial, in): ")
    n = prompt_int("Number of bricks per ring (N): ")
    brick_face = prompt_float("Brick outer face length (in): ")
    saw_kerf = prompt_float("Saw kerf / blade width (in): ")

    generate_brick_template(
        barrel_diameter_in=barrel_diameter,
        brick_thickness_in=brick_thickness,
        num_bricks=n,
        desired_brick_face_in=brick_face,
        saw_kerf_in=saw_kerf,
        barrel_wall_thickness_in=barrel_wall,
        insulation_thickness_in=insulation
    )

