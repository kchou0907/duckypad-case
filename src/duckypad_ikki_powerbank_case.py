import math
import cadquery as cq
from cadquery import exporters
from pathlib import Path

# -----------------------------------------------------------------------------
# duckyPad Pro + INIU P781 desk case
# Parametric first-print prototype
# Units: mm
# -----------------------------------------------------------------------------

# ---- Ikki68 Aurora R2-inspired exterior ----
TYPING_ANGLE_DEG = 6.5
OUTER_W = 122.0
OUTER_D = 112.0                 # ~4.4 in, intentionally Ikki68-ish depth
FRONT_BODY_H = 22.86            # 0.9 in; easy to change after physical comparison
OUTER_CORNER_R = 7.0
WALL = 3.0
FLOOR_T = 2.4

# ---- duckyPad Pro PCB (official Eagle board geometry) ----
PCB_W = 109.0
PCB_D = 96.0
PCB_T = 1.6
PCB_CORNER_R = 3.5
PCB_X = 4.0
PCB_Y = 12.0
# PCB underside at its FRONT edge. This plane tilts 6.5 degrees toward the rear.
PCB_FRONT_Z = 21.5

# M2 mounting holes from the official board file, local PCB coordinates.
PCB_M2_HOLES = [
    (38.5, 19.5), (57.5, 76.5), (38.5, 76.5),
    (57.5, 57.5), (57.5, 38.5), (38.5, 57.5),
    (38.5, 38.5), (57.5, 19.5), (99.0, 76.5),
    (19.5, 76.5), (19.5, 38.5), (19.5, 57.5),
    (19.5, 19.5),
]
POST_OD = 6.0
POST_PILOT_D = 3.2             # M2 heat-set insert pocket (typ. 3.0-3.2 mm OD)
POST_PILOT_DEPTH = 4.0

# ---- INIU SnapGo Air P781 nominal body ----
PB_W = 71.0                    # short edge containing ports/display
PB_L = 105.0
PB_H = 13.7
PB_CLEAR_X = 0.8               # total pocket extra width
PB_CLEAR_Y = 0.8               # total pocket extra length
PB_X = 46.5                    # tune this to align a USB-C port with duckyPad upper USB-C
PB_Y = 2.8                     # battery slides in from rear; rear edge ~= 108.6
PB_GUIDE_H = 3.0
PB_GUIDE_T = 1.5
PB_FLOOR_PAD = 0.5             # reserved for thin foam/tape; model stays on main floor

# Optional low anti-slide lip. The U-shaped USB connector will also retain the bank.
LIP_T_Y = 2.8
LIP_LOW_H = 2.2
LIP_SIDE_TAB_H = 6.0
LIP_SIDE_TAB_W = 1.0

# Side USB access (lower/right duckyPad USB-C)
SIDE_USB_Y_LOCAL = 26.416
SIDE_USB_OPEN_Y = 18.0
SIDE_USB_OPEN_Z = 12.0

# Rear USB access (upper power USB-C)
UPPER_USB_X_LOCAL = 87.0
UPPER_USB_Y_LOCAL = 92.127
UPPER_USB_CHIMNEY_W = 21.0

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
angle = math.radians(TYPING_ANGLE_DEG)
S = math.sin(angle)
C = math.cos(angle)
T = math.tan(angle)
REAR_BODY_H = FRONT_BODY_H + OUTER_D * T
PB_POCKET_W = PB_W + PB_CLEAR_X
PB_POCKET_L = PB_L + PB_CLEAR_Y
PB_LEFT = PB_X - PB_CLEAR_X / 2
PB_RIGHT = PB_X + PB_W + PB_CLEAR_X / 2
PB_FRONT = PB_Y - PB_CLEAR_Y / 2
PB_REAR = PB_Y + PB_L + PB_CLEAR_Y / 2


def rounded_prism(w, d, h, r, x=0, y=0, z=0):
    """Rounded XY rectangle, extruded vertically."""
    wp = cq.Workplane("XY").workplane(offset=z).center(x + w/2, y + d/2)
    solid = wp.rect(w, d).extrude(h)
    # Fillet only vertical edges for a rounded footprint.
    if r > 0:
        solid = solid.edges("|Z").fillet(r)
    return solid


def wedge(width, depth, front_h, angle_deg, x=0, y=0, z0=0):
    """Desk-flat bottom; top rises toward +Y at angle_deg."""
    rear_h = front_h + depth * math.tan(math.radians(angle_deg))
    prof = (
        cq.Workplane("YZ")
        .moveTo(y, z0)
        .lineTo(y + depth, z0)
        .lineTo(y + depth, z0 + rear_h)
        .lineTo(y, z0 + front_h)
        .close()
        .extrude(width)
        .translate((x, 0, 0))
    )
    return prof


def outer_wedge():
    prism = rounded_prism(OUTER_W, OUTER_D, REAR_BODY_H + 1.0, OUTER_CORNER_R)
    wed = wedge(OUTER_W, OUTER_D, FRONT_BODY_H, TYPING_ANGLE_DEG)
    return prism.intersect(wed)


def pcb_yz(local_y):
    """Projected desk coordinates of a point on the tilted PCB underside."""
    gy = PCB_Y + local_y * C
    gz = PCB_FRONT_Z + local_y * S
    return gy, gz


def pcb_global(local_x, local_y):
    gy, gz = pcb_yz(local_y)
    return PCB_X + local_x, gy, gz


def point_in_pb_xy(x, y, margin=0):
    return (PB_LEFT-margin <= x <= PB_RIGHT+margin and
            PB_FRONT-margin <= y <= PB_REAR+margin)


def sloped_strip(x0, x1, y0, y1, zfront_at_y0, thickness):
    """Vertical-thickness strip whose top follows case angle."""
    depth = y1 - y0
    z1 = zfront_at_y0
    z2 = z1 + depth * T
    profile = (
        cq.Workplane("YZ")
        .moveTo(y0, z1 - thickness)
        .lineTo(y1, z2 - thickness)
        .lineTo(y1, z2)
        .lineTo(y0, z1)
        .close()
        .extrude(x1-x0)
        .translate((x0, 0, 0))
    )
    return profile


def axis_y_cylinder(x, y_start, z, length, diameter):
    # XZ plane normal is +/-Y; extrude along Y.
    return (
        cq.Workplane("XZ", origin=(x, y_start, z))
        .circle(diameter/2)
        .extrude(length)
    )

# -----------------------------------------------------------------------------
# Main body
# -----------------------------------------------------------------------------
body = outer_wedge()

# Hollow the shell while preserving a full floor.
inner = rounded_prism(
    OUTER_W - 2*WALL,
    OUTER_D - 2*WALL,
    REAR_BODY_H + 15.0,
    max(1.0, OUTER_CORNER_R - WALL),
    x=WALL,
    y=WALL,
    z=FLOOR_T,
)
body = body.cut(inner)

# Guaranteed rectangular clearance tunnel for the power bank. This removes any
# intrusion from the shell's rounded rear corners while preserving the floor.
pb_tunnel = cq.Workplane("XY").box(
    PB_POCKET_W, OUTER_D-PB_FRONT+2.0, PB_H+2.5,
    centered=(False, False, False)
).translate((PB_LEFT, PB_FRONT, FLOOR_T))
body = body.cut(pb_tunnel)

# Battery side guides and front stop. The rear is intentionally open for sliding access.
# Left/right rails
for gx in (PB_LEFT - PB_GUIDE_T, PB_RIGHT):
    rail = cq.Workplane("XY").box(
        PB_GUIDE_T, PB_POCKET_L, PB_GUIDE_H,
        centered=(False, False, False)
    ).translate((gx, PB_FRONT, FLOOR_T))
    body = body.union(rail)
# Front stop
front_stop = cq.Workplane("XY").box(
    PB_POCKET_W + 2*PB_GUIDE_T, PB_GUIDE_T, PB_GUIDE_H,
    centered=(False, False, False)
).translate((PB_LEFT-PB_GUIDE_T, PB_FRONT-PB_GUIDE_T, FLOOR_T))
body = body.union(front_stop)

# PCB mounting posts: retain only posts whose footprint does not collide with the battery.
active_posts = []
for lx, ly in PCB_M2_HOLES:
    gx, gy, gz = pcb_global(lx, ly)
    # Require post OD plus a little tolerance outside the battery pocket.
    if point_in_pb_xy(gx, gy, POST_OD/2 + 0.5):
        continue
    # Also keep posts clear of the shell walls.
    if gx < WALL + POST_OD/2 or gx > OUTER_W-WALL-POST_OD/2:
        continue
    h = gz - FLOOR_T + 1.0
    if h <= 2:
        continue
    post = cq.Workplane("XY").workplane(offset=FLOOR_T).center(gx, gy).circle(POST_OD/2).extrude(h)
    # Trim the post to the exact 6.5-degree PCB underside plane so the PCB rests flat.
    pcb_plane_front_at_y0 = PCB_FRONT_Z - PCB_Y*T
    support_halfspace = wedge(OUTER_W, OUTER_D, pcb_plane_front_at_y0, TYPING_ANGLE_DEG)
    post = post.intersect(support_halfspace)
    # Blind heat-set pocket from the top.
    pilot = cq.Workplane("XY").workplane(offset=max(FLOOR_T, gz-POST_PILOT_DEPTH)).center(gx, gy).circle(POST_PILOT_D/2).extrude(POST_PILOT_DEPTH+1.2)
    post = post.cut(pilot)
    body = body.union(post)
    active_posts.append((lx, ly, gx, gy, gz))

# Right-edge PCB support rail, interrupted around the side USB-C connector.
# Rail top follows the actual PCB tilt (sin) very closely; using tan here is <0.1 mm diff over length.
rail_x0 = PCB_X + PCB_W - 1.8
rail_x1 = OUTER_W - WALL
board_rear_proj = PCB_Y + PCB_D*C
rail_t = 1.4
# Front segment
usb_gy, usb_gz = pcb_yz(SIDE_USB_Y_LOCAL)
seg1_y0 = PCB_Y + 3
seg1_y1 = usb_gy - SIDE_USB_OPEN_Y/2 - 1.5
if seg1_y1 > seg1_y0:
    ztop = PCB_FRONT_Z + (seg1_y0-PCB_Y)*math.tan(angle)
    body = body.union(sloped_strip(rail_x0, rail_x1, seg1_y0, seg1_y1, ztop, rail_t))
# Rear segment
seg2_y0 = usb_gy + SIDE_USB_OPEN_Y/2 + 1.5
seg2_y1 = board_rear_proj - 2
if seg2_y1 > seg2_y0:
    ztop = PCB_FRONT_Z + (seg2_y0-PCB_Y)*math.tan(angle)
    body = body.union(sloped_strip(rail_x0, rail_x1, seg2_y0, seg2_y1, ztop, rail_t))

# Rear I/O bay: expose the entire battery port/display edge.
low_open_z0 = FLOOR_T - 0.4
low_open_h = PB_H + 5.2
low_open = cq.Workplane("XY").box(
    PB_POCKET_W + 5.0, WALL + 5.0, low_open_h,
    centered=(False, False, False)
).translate((PB_LEFT-2.5, OUTER_D-WALL-1.0, low_open_z0))
body = body.cut(low_open)

# Tall narrow chimney for the U-shaped USB-C adapter to the duckyPad upper USB port.
upper_usb_x = PCB_X + UPPER_USB_X_LOCAL
upper_usb_y, upper_usb_z = pcb_yz(UPPER_USB_Y_LOCAL)
chimney = cq.Workplane("XY").box(
    UPPER_USB_CHIMNEY_W, WALL+7.0, REAR_BODY_H,
    centered=(False, False, False)
).translate((upper_usb_x-UPPER_USB_CHIMNEY_W/2, OUTER_D-WALL-2.0, PB_H+FLOOR_T+1.5))
body = body.cut(chimney)

# Right-side access tunnel for duckyPad's second USB-C port.
side_open = cq.Workplane("XY").box(
    WALL+14.0, SIDE_USB_OPEN_Y, SIDE_USB_OPEN_Z,
    centered=(False, False, False)
).translate((OUTER_W-WALL-9.0, usb_gy-SIDE_USB_OPEN_Y/2, usb_gz-SIDE_USB_OPEN_Z/2))
body = body.cut(side_open)

# Shallow rubber-foot recesses on the underside.
for fx, fy in ((9,9), (OUTER_W-9,9), (9,OUTER_D-9), (OUTER_W-9,OUTER_D-9)):
    recess = cq.Workplane("XY").workplane(offset=-0.01).center(fx,fy).circle(4.0).extrude(0.9)
    body = body.cut(recess)

# -----------------------------------------------------------------------------
# Optional rear anti-slide lip.
# It only overlaps the lowest ~2 mm of the bank and leaves ports/display visible.
# The narrow side tabs sit just outside the battery pocket; sand for a snug friction fit.
# -----------------------------------------------------------------------------
lip_y0 = OUTER_D - LIP_T_Y - 0.3
lip = cq.Workplane("XY").box(
    PB_POCKET_W + 2.0, LIP_T_Y, LIP_LOW_H,
    centered=(False, False, False)
).translate((PB_LEFT-1.0, lip_y0, FLOOR_T))
for tx in (PB_LEFT-1.0, PB_RIGHT):
    tab = cq.Workplane("XY").box(
        LIP_SIDE_TAB_W, LIP_T_Y, LIP_SIDE_TAB_H,
        centered=(False, False, False)
    ).translate((tx, lip_y0, FLOOR_T))
    lip = lip.union(tab)

# -----------------------------------------------------------------------------
# Simple reference solids for assembly preview (NOT for printing)
# -----------------------------------------------------------------------------
# PCB rounded rectangle, rotated physically by 6.5 degrees.
pcb = rounded_prism(PCB_W, PCB_D, PCB_T, PCB_CORNER_R)
pcb = pcb.rotate((0,0,0), (1,0,0), TYPING_ANGLE_DEG).translate((PCB_X, PCB_Y, PCB_FRONT_Z))

# Power bank envelope. Flat on floor; clearance envelope uses actual nominal body size.
pb = rounded_prism(PB_W, PB_L, PB_H, 5.0, x=PB_X, y=PB_Y, z=FLOOR_T+PB_FLOOR_PAD)

# A slim dummy top plate to show original assembly height (approx only).
top_plate = rounded_prism(PCB_W, PCB_D, 1.5, PCB_CORNER_R)
top_plate = top_plate.rotate((0,0,0), (1,0,0), TYPING_ANGLE_DEG).translate((PCB_X, PCB_Y, PCB_FRONT_Z + 5.6))

assembly = cq.Compound.makeCompound([
    body.val(), lip.val(), pcb.val(), pb.val(), top_plate.val()
])

# Rear fit-test slice: last 20 mm of case, useful before committing to a full print.
slice_box = cq.Workplane("XY").box(OUTER_W+4, 20.0, REAR_BODY_H+10, centered=(False,False,False)).translate((-2, OUTER_D-20, 0))
rear_fit = body.intersect(slice_box)

# -----------------------------------------------------------------------------
# Export
# -----------------------------------------------------------------------------
OUT = Path(__file__).resolve().parent / "duckypad_case_exports"
OUT.mkdir(exist_ok=True)

for name, obj in {
    "duckypad_case_body": body,
    "optional_battery_lip": lip,
    "rear_fit_test": rear_fit,
}.items():
    exporters.export(obj, str(OUT / f"{name}.step"))
    exporters.export(obj, str(OUT / f"{name}.stl"), tolerance=0.08, angularTolerance=0.15)

exporters.export(assembly, str(OUT / "assembly_preview.step"))

# Save active-post report for easy verification / remixing.
with open(OUT / "active_mounts.txt", "w", encoding="utf-8") as f:
    f.write("Active duckyPad PCB M2 mounting posts (local_x, local_y -> global x,y,z):\n")
    for row in active_posts:
        f.write(f"{row[0]:.1f}, {row[1]:.1f} -> {row[2]:.2f}, {row[3]:.2f}, {row[4]:.2f}\n")

print(f"Exported to: {OUT}")
print(f"Body bbox: {body.val().BoundingBox().xlen:.2f} x {body.val().BoundingBox().ylen:.2f} x {body.val().BoundingBox().zlen:.2f}")
print(f"Rear body height: {REAR_BODY_H:.2f}")
print(f"Battery pocket: x {PB_LEFT:.2f}..{PB_RIGHT:.2f}, y {PB_FRONT:.2f}..{PB_REAR:.2f}")
print(f"Active PCB posts: {len(active_posts)}")
for p in active_posts:
    print("  ", p)