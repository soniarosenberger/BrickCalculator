# Author: Sonia Rosenberger
# Date: January 17, 2026
# Purpose: Draw a template for an N-sided refractory brick lining inside a barrel:
#          (1) a top-view full ring layout with key diameters and (2) a single-brick cut template
#          with dimensions and miter angle callouts. Prints computed geometry to the terminal.
# Usage: Run as a script. Adjust the "INPUTS" section at the bottom as needed.

import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Arc


# ---------- Helpers ----------

def dim(ax, p1, p2, offset=(0, 0), text="", text_offset=(0, 0), lw=1):
    """Engineering-style dimension with extension lines and <-> arrows."""
    offset_x, offset_y = offset
    q1 = (p1[0] + offset_x, p1[1] + offset_y)
    q2 = (p2[0] + offset_x, p2[1] + offset_y)

    ax.plot([p1[0], q1[0]], [p1[1], q1[1]], lw=lw)
    ax.plot([p2[0], q2[0]], [p2[1], q2[1]], lw=lw)

    ax.annotate(
        "",
        xy=q2, xytext=q1,
        arrowprops=dict(arrowstyle="<->", lw=lw, shrinkA=0, shrinkB=0)
    )

    text_x = (q1[0] + q2[0]) / 2 + text_offset[0]
    text_y = (q1[1] + q2[1]) / 2 + text_offset[1]
    ax.text(text_x, text_y, text, fontsize=10, ha="center", va="center")


def angle_arc(ax, center, start_deg, end_deg, radius, label, label_angle=None, lw=1):
    """Arc + label for an angle callout."""
    arc = Arc(center, 2 * radius, 2 * radius, theta1=start_deg, theta2=end_deg, lw=lw)
    ax.add_patch(arc)

    if label_angle is None:
        label_angle = (start_deg + end_deg) / 2

    tx = center[0] + 1.25 * radius * math.cos(math.radians(label_angle))
    ty = center[1] + 1.25 * radius * math.sin(math.radians(label_angle))
    ax.text(tx, ty, label, fontsize=10, ha="center", va="center")


def plot_circle(ax, radius, lw=1):
    """Plot a circle of a given radius using 0..360 degree sampling."""
    xs = [radius * math.cos(math.radians(deg)) for deg in range(361)]
    ys = [radius * math.sin(math.radians(deg)) for deg in range(361)]
    ax.plot(xs, ys, lw=lw)


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


def draw_miter_callout(
    ax,
    corner_pt,
    square_reference_deg,
    arc_start_deg,
    arc_end_deg,
    label_text,
    label_angle_deg,
    ref_line_len,
    arc_radius,
    lw=1
):
    """Draw dashed vertical reference line and an angle arc/label for a miter callout."""
    # dashed vertical reference
    ax.plot(
        [corner_pt[0], corner_pt[0]],
        [corner_pt[1], corner_pt[1] - ref_line_len],
        linestyle="--",
        linewidth=1
    )

    # miter arc + label
    angle_arc(
        ax, corner_pt,
        start_deg=arc_start_deg,
        end_deg=arc_end_deg,
        radius=arc_radius,
        label=label_text,
        label_angle=label_angle_deg,
        lw=lw
    )


def tweak_last_two_angle_labels(ax, label_font_size, right_dx_dy, left_dx_dy):
    """Match the original post-processing: shrink font and manually nudge left/right labels."""
    # Reduce label font size manually (overwrite default inside angle_arc)
    for txt in ax.texts[-2:]:
        txt.set_fontsize(label_font_size)

    # Right side label is the most recent one added
    right_label = ax.texts[-1]
    rx, ry = right_label.get_position()
    right_label.set_position((rx + right_dx_dy[0], ry + right_dx_dy[1]))
    right_label.set_fontsize(label_font_size)

    # Left side label is the one just before that
    left_label = ax.texts[-2]
    lx, ly = left_label.get_position()
    left_label.set_position((lx + left_dx_dy[0], ly + left_dx_dy[1]))
    left_label.set_fontsize(label_font_size)


# ---------- Main ----------
def draw_fixed(barrel_diameter_in, brick_thickness_in, num_bricks_per_ring, outer_face_in, saw_kerf_in):
    """
    Inputs:
        barrel_diameter_in: inside diameter of barrel (in)
        brick_thickness_in: radial lining thickness (in)
        num_bricks_per_ring: number of bricks per ring
        outer_face_in: finished outer face length of brick (in)
        saw_kerf_in: blade width (in)
    """

    # Radii
    barrel_inner_radius_in = barrel_diameter_in / 2.0
    lining_inner_radius_in = barrel_inner_radius_in - brick_thickness_in
    if lining_inner_radius_in <= 0:
        raise ValueError("Brick thickness is too large for this barrel diameter.")

    # Angles
    central_angle_deg = 360.0 / num_bricks_per_ring
    miter_angle_deg = 180.0 / num_bricks_per_ring  # off-square per end
    miter_angle_rad = math.radians(miter_angle_deg)

    # Brick face lengths (outer is fixed)
    outer_face_len_in = float(outer_face_in)

    # Inner face from wedge geometry (straight end cuts)
    inner_face_len_in = outer_face_len_in - 2.0 * brick_thickness_in * math.tan(miter_angle_rad)
    if inner_face_len_in <= 0:
        raise ValueError("Inner face computed <= 0. With these inputs, this wedge is not possible.")

    # Taper/inset per side
    taper_each_side_in = (outer_face_len_in - inner_face_len_in) / 2.0

    # Clear opening for regular N-gon inner boundary
    clear_id_across_corners_in = 2.0 * lining_inner_radius_in
    clear_id_across_flats_in = 2.0 * lining_inner_radius_in * math.cos(math.pi / num_bricks_per_ring)

    # Plotting 
    fig, (ax_ring, ax_cut) = plt.subplots(1, 2, figsize=(13.8, 6.3))
    fig.suptitle(f"Template for {num_bricks_per_ring}-Sided Brick Lining", fontsize=14)

    # -------- LEFT: Full ring --------
    ax_ring.set_aspect("equal", adjustable="box")
    ax_ring.axis("off")
    ax_ring.set_title("Top View", fontsize=12)

    # Outer circle (barrel inner wall)
    plot_circle(ax_ring, barrel_inner_radius_in, lw=1)

    # Inner boundary reference: vertex circle (corners)
    plot_circle(ax_ring, lining_inner_radius_in, lw=1)

    # Inscribed circle (across-flats) (true clearance)
    lining_incircle_radius_in = lining_inner_radius_in * math.cos(math.pi / num_bricks_per_ring)
    plot_circle(ax_ring, lining_incircle_radius_in, lw=1)

    # Wedge bricks (regular N-gon layout)
    draw_wedge_bricks(ax_ring, lining_inner_radius_in, barrel_inner_radius_in, num_bricks_per_ring)

    # -------- Diameter dimensions (BOTTOM STACKED, more vertical spacing) --------
    dims_base_y = -(barrel_inner_radius_in + 1.35)   # Spacing
    dims_stack_gap = 1.8                            # Spacing

    y_barrel_dim = dims_base_y
    y_clear_flats_dim = dims_base_y - dims_stack_gap
    y_clear_corners_dim = dims_base_y - 2 * dims_stack_gap

    # Barrel inside diameter (outer circle)
    dim(
        ax_ring,
        (-barrel_inner_radius_in, y_barrel_dim), (barrel_inner_radius_in, y_barrel_dim),
        text=f"Ø {barrel_diameter_in:.3f} in  (Barrel diameter)",
        text_offset=(0, -0.7)
    )

    # Clear opening across flats (MIN clearance) — its own dimension line
    dim(
        ax_ring,
        (-clear_id_across_flats_in / 2.0, y_clear_flats_dim), (clear_id_across_flats_in / 2.0, y_clear_flats_dim),
        text=f"Ø {clear_id_across_flats_in:.3f} in  (Inner diameter across flats)",
        text_offset=(0, -0.7)
    )

    # Optional: Clear opening across corners (MAX) — its own dimension line
    dim(
        ax_ring,
        (-clear_id_across_corners_in / 2.0, y_clear_corners_dim), (clear_id_across_corners_in / 2.0, y_clear_corners_dim),
        text=f"Ø {clear_id_across_corners_in:.3f} in  (Inner diameter across corners)",
        text_offset=(0, -0.7)
    )

    plot_limit_in = barrel_inner_radius_in + 2.2  # Spacing
    ax_ring.set_xlim(-plot_limit_in, plot_limit_in)
    ax_ring.set_ylim(-(plot_limit_in + 4.0), plot_limit_in)  # Spacing

    # -------- RIGHT: Single brick cut template --------
    ax_cut.set_aspect("equal", adjustable="box")
    ax_cut.axis("off")

    # ----- Center right title over brick geometry -----
    brick_center_x = outer_face_len_in / 2
    title_y = brick_thickness_in + 4.15  # Spacing

    ax_cut.text(
        brick_center_x,
        title_y,
        "Single Brick - CUT TEMPLATE",
        fontsize=12,
        ha="center",
        va="bottom",
        transform=ax_cut.transData
    )

    # Trapezoid laid flat (outer face horizontal)
    outer_left_pt = (0.0, brick_thickness_in)  # outer-left
    outer_right_pt = (outer_face_len_in, brick_thickness_in)  # outer-right
    inner_right_pt = (taper_each_side_in + inner_face_len_in, 0.0)  # inner-right
    inner_left_pt = (taper_each_side_in, 0.0)  # inner-left

    ax_cut.add_patch(Polygon([outer_left_pt, outer_right_pt, inner_right_pt, inner_left_pt], closed=True, fill=False, lw=2))

    dim(
        ax_cut,
        outer_left_pt, outer_right_pt,
        offset=(0, 0.9),
        text=f"{outer_face_len_in:.3f} in  (Outer face)",
        text_offset=(0, 0.25)
    )

    dim(
        ax_cut,
        inner_left_pt, inner_right_pt,
        offset=(0, -0.9),
        text=f"{inner_face_len_in:.3f} in  (Inner face)",
        text_offset=(0, -0.25)
    )

    dim(
        ax_cut,
        (outer_face_len_in, 0.0), (outer_face_len_in, brick_thickness_in),
        offset=(1.3, 0),
        text=f"{brick_thickness_in:.3f} in  (Thickness)",
        text_offset=(0.25, -1)
    )

    dim(
        ax_cut,
        (0.0, 0.0), (taper_each_side_in, 0.0),
        offset=(0, -1.6),
        text=f"{taper_each_side_in:.3f} in  (Taper each side)",
        text_offset=(0, -0.25)
    )

    # ----- Miter angle callouts with dashed square reference lines -----
    square_reference_deg = 270.0  # vertical downward reference

    left_cut_angle_deg = square_reference_deg + miter_angle_deg
    right_cut_angle_deg = square_reference_deg - miter_angle_deg

    ref_line_len = 1.4   # Spacing
    arc_radius = 0.9     # Spacing
    label_font_size = 8  # Spacing

    # LEFT SIDE callout
    draw_miter_callout(
        ax=ax_cut,
        corner_pt=outer_left_pt,
        square_reference_deg=square_reference_deg,
        arc_start_deg=square_reference_deg,
        arc_end_deg=left_cut_angle_deg,
        label_text=f"{miter_angle_deg:.2f}°",
        label_angle_deg=square_reference_deg + miter_angle_deg / 2,
        ref_line_len=ref_line_len,
        arc_radius=arc_radius,
        lw=1
    )

    # RIGHT SIDE callout (short direction — swapped order)
    draw_miter_callout(
        ax=ax_cut,
        corner_pt=outer_right_pt,
        square_reference_deg=square_reference_deg,
        arc_start_deg=right_cut_angle_deg,
        arc_end_deg=square_reference_deg,
        label_text=f"{miter_angle_deg:.2f}°",
        label_angle_deg=square_reference_deg - miter_angle_deg / 2,
        ref_line_len=ref_line_len,
        arc_radius=arc_radius,
        lw=1
    )

    # Match original manual label tweaks precisely
    tweak_last_two_angle_labels(
        ax=ax_cut,
        label_font_size=label_font_size,
        right_dx_dy=(0.50, -0.05),
        left_dx_dy=(-0.50, -0.05)
    )

    ax_cut.text(
        outer_face_len_in / 2,
        brick_thickness_in + 2.05,  # Spacing
        f"Miter per end = {miter_angle_deg:.2f}° (off-square)\n"
        f"Central angle = {central_angle_deg:.2f}°\n"
        f"Saw kerf = {saw_kerf_in:.3f} in",
        fontsize=9.7, ha="center", va="center"
    )

    ax_cut.set_xlim(-2.0, outer_face_len_in + 5.5)  # Spacing
    ax_cut.set_ylim(-3.0, brick_thickness_in + 3.0)  # Spacing

    # -------- Terminal output --------
    print("\n=== INPUTS ===")
    print(f"N:                     {num_bricks_per_ring}")
    print(f"Barrel inner diameter:             {barrel_diameter_in:.3f} in")
    print(f"Brick thickness:       {brick_thickness_in:.3f} in")
    print(f"Outer face length:       {outer_face_len_in:.3f} in")
    print(f"Saw kerf:       {saw_kerf_in:.3f} in")

    print("\n=== OUTPUTS ===")
    print(f"Central angle:       {central_angle_deg:.3f}°")
    print(f"Miter angle per end:   {miter_angle_deg:.3f}° (off-square)")
    print(f"Inner face:       {inner_face_len_in:.3f} in")
    print(f"Taper per side:       {taper_each_side_in:.3f} in")
    print(f"Inner diameter across flats:  {clear_id_across_flats_in:.3f} in")
    print(f"Inner diameter across corners:{clear_id_across_corners_in:.3f} in")

    plt.tight_layout()
    plt.show()


# ============================ INPUTS ============================
BARREL_DIAMETER_IN = 24          # inside diameter of barrel
BRICK_THICKNESS_IN = 4.5         # lining thickness (thickness of one brick, inward)
N = 8                            # bricks per ring
BRICK_OUTER_FACE_IN = 9.0        # length of outer face of one brick
SAW_KERF_IN = 0.125              # saw blade width

draw_fixed(BARREL_DIAMETER_IN, BRICK_THICKNESS_IN, N, BRICK_OUTER_FACE_IN, SAW_KERF_IN)
