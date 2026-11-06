"""Shared places for ep125 (make_story.py and set.py). Metres, z up. A character facing -y has yaw 0, +x 90, +y 180,
-x -90.

THE COURT: house k (1..12) stands at angle A0 + (k-1)*DA (from +y toward +x) on a ring of radius R round the
fountain at the origin, its door facing the fountain. House-local frame: lx along the facade (+lx is on the right of
a camera standing in front of the door), d is the distance out of the wall toward the fountain, z up. The porch is a
landing (z 0.45, d 0 to 0.9) and two steps (z 0.30 at d 0.9 to 1.3, z 0.15 at d 1.3 to 1.7).

THE ROOM: one closed room at ROOM with five stages along its walls (shop, kitchen, my room, the old room, the hall),
each lit by its own steady lamp. THE WINDOW: Mr. Ames's window and armchair at WIN.
"""
import math

R = 11.0
A0 = -125.0
DA = 250.0 / 11
ROOM = (40.0, 0.0)
WIN = (80.0, 0.0)
LAND = 0.45          # the landing's height
STEP_Z = {0: 0.45, 1: 0.30, 2: 0.15}

# who lives where
LOU, ME, AMES, HADDAD = 1, 7, 3, 5


def ang(k):
    return A0 + (k - 1) * DA


def hw(k, lx, d, z=0.0):
    """House-local (lx along the facade, d out toward the fountain, z up) to world."""
    a = math.radians(ang(k))
    ox, oy, rz = R * math.sin(a), R * math.cos(a), -a
    ly = -d
    c, s = math.cos(rz), math.sin(rz)
    return [round(ox + lx * c - ly * s, 3), round(oy + lx * s + ly * c, 3), z]


def yawf(k):
    """A character facing the house."""
    return 180 - ang(k)


def yawc(k):
    """A character facing out, toward the fountain."""
    return -ang(k)


def yaw_to(p, q):
    return math.degrees(math.atan2(q[0] - p[0], -(q[1] - p[1])))


# ---- the room: stage origins are the wall point each stage hangs on, ROOM-relative
RX, RY = ROOM
WALL_N, WALL_S, WALL_E = RY + 6.0, RY - 6.0, RX + 8.0
STAGE = {
    "shop": (RX - 4.0, WALL_N),      # camera looks +y
    "kitchen": (RX + 4.0, WALL_N),   # camera looks +y
    "mine": (RX - 4.0, WALL_S),      # camera looks -y
    "old": (RX + 4.0, WALL_S),       # camera looks -y
    "hall": (WALL_E, RY),            # camera looks +x
}
