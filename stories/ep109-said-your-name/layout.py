"""Shared places for ep109 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0,
+x 90, +y 180, -x -90. Four places a long way apart, so a camera never sees the next one."""
import math

K = (-80.0, 0.0)            # our kitchen (the room is 12 x 9; the island with the radio stands in the middle)
RAD = (-81.2, 2.2)          # the radio on the island, its front toward -y
COUNTER_Z = 0.92
ME_K = (-81.2, 3.05)        # me, behind the island
NB_X = -96.0                # the neighbor's wall across the street from our kitchen window
FRIDGE = (-76.4, 3.35)      # the fridge's front face

WIN_Z = (4.3, 5.9)          # upper windows on every shop: sill and top
FACE_Z = 3.5                # a character's feet when its face is at an upper window
SHOP_X = [28.0 + 8.0 * i for i in range(11)]       # shop centres, each 8 wide, fronts at y = 5.0
NY = 5.0                    # the north row's face
BAKERY = 52.0
CAFE = 76.0
TABLE = (75.3, 6.6)         # the cafe window table
SEAT_ME = (74.55, 6.6)
SEAT_DEV = (76.15, 6.6)
STALL = (70.0, 3.6)
SHELTER = (50.0, -5.6)
BUS_Y = -2.6
BENCH = (86.0, -8.5)        # faces +y
SPOT = (60.0, 3.0)          # where my bag tears
OD = 150.0                  # Mrs. Odell's house, centre x; its front is at y = 5.0, deck at z = 0.3
DECK_Z = 0.3
SW = 3.4                    # ground storey height
UP = 6.8                    # top of the upper storey

def win_xs(cx):
    return [cx - 2.0, cx + 2.0]

def yaw_to(src, dst):
    dx, dy = dst[0] - src[0], dst[1] - src[1]
    return math.degrees(math.atan2(dx, -dy))


# ------------------------------------------------------------------------------------------ the oranges (pure python)
N_ORANGES = 9
ORANGE_R = 0.11
ORANGE_GROUND = 0.05 + ORANGE_R


def orange_start(i):
    """Where orange i leaves the bag (the bag hangs at my side, hand-high 0.62 m, bottom 0.2 m)."""
    return (SPOT[0] + 0.35 + 0.05 * (i % 3), SPOT[1] - 0.1 + 0.04 * (i % 2), 0.3 + 0.04 * (i % 3))


def orange_release(i):
    """Seconds after the tear that orange i leaves the bag."""
    return 0.0 + 0.11 * i


_ANG = [-8, 28, 70, 118, 160, -50, 205, 250, -100]          # degrees, 0 = east, 90 = north
_SPD = [2.6, 2.2, 1.5, 1.9, 2.5, 2.0, 1.7, 2.3, 1.9]
_TRAJ = {}


def orange_traj(i, T=14.0):
    """The orange's path in 1/60 s steps from its release: a few bounces, then it rolls to a stop. A wall at y = 4.8."""
    if i in _TRAJ:
        return _TRAJ[i]
    x, y, z = orange_start(i)
    a = math.radians(_ANG[i])
    vx, vy, vz = _SPD[i] * math.cos(a), _SPD[i] * math.sin(a), 0.4
    out = []
    dt = 1.0 / 60
    for _ in range(int(T / dt)):
        out.append((x, y, z))
        vz -= 9.8 * dt
        x, y, z = x + vx * dt, y + vy * dt, z + vz * dt
        if y > 4.8:
            y, vy = 4.8, -0.4 * abs(vy)
        if z < ORANGE_GROUND:
            z = ORANGE_GROUND
            if abs(vz) > 0.7:
                vz = -vz * 0.5
                vx *= 0.85
                vy *= 0.85
            else:
                vz = 0.0
        if z <= ORANGE_GROUND + 1e-6 and vz == 0.0:
            sp = math.hypot(vx, vy)
            if sp > 0:
                ns = max(0.0, sp - 0.75 * dt)
                vx, vy = vx * ns / sp, vy * ns / sp
    _TRAJ[i] = out
    return out


def orange_at(i, dt):
    tr = orange_traj(i)
    k = min(len(tr) - 1, max(0, int(dt * 60)))
    return tr[k]


def orange_final(i):
    return orange_traj(i)[-1]
