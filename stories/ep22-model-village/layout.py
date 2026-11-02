"""Where things are in ep22's world (metres), shared by set.py (Blender) and generator/make_story.py (plain
Python). Z is up, -y is toward the path and the camera, +y goes up the hill. A character with yaw 0 faces -y."""
import math

ROWS = 6
ROW_DY = 1.3            # each terrace of the model is 1.3 m deep and 0.1 m above the one before
XMIN, XMAX = -2.9, 2.9
FRONT = 0.62            # the houses' front faces, in from each terrace's front edge
WALL = 0.012
FLOOR_T = 0.03
SILL, WIN_W, WIN_H = 0.02, 0.075, 0.065
H_BODY = 0.26


def row_y(i):
    return ROW_DY * i


def top_z(i):
    return 0.20 + 0.10 * i


# the six rooms we see into: row, centre x, width, depth, window offset from the centre
ROOMS = {
    "bakery": dict(row=0, cx=2.15, w=0.52, d=0.50, wx=-0.07, wall="#e8dfc4", roof="#4b5057"),
    "blue": dict(row=1, cx=1.35, w=0.46, d=0.50, wx=0.07, wall="#aebfce", roof="#5a4d45"),
    "chapel": dict(row=3, cx=-0.95, w=0.62, d=0.60, wx=0.0, wall="#d9d4c6", roof="#3e444c"),
    "next": dict(row=4, cx=-1.25, w=0.46, d=0.50, wx=0.07, wall="#dcaeb0", roof="#4b5057"),
    "cottage": dict(row=4, cx=-1.95, w=0.46, d=0.50, wx=0.07, wall="#e3cfa7", roof="#6a6e74"),
    "tea": dict(row=5, cx=0.35, w=0.80, d=0.62, wx=-0.18, wall="#e6dcc0", roof="#4b5057"),
}


def room(name):
    r = dict(ROOMS[name])
    r["front_y"] = row_y(r["row"]) + FRONT
    r["floor_z"] = top_z(r["row"]) + FLOOR_T
    r["win_x"] = r["cx"] + r["wx"]
    r["win_z"] = r["floor_z"] + SILL + WIN_H / 2
    return r


def stand(name, back=0.03):
    """Where the Resident stands in a room: just inside its window."""
    r = room(name)
    return [round(r["win_x"], 4), round(r["front_y"] + WALL + back, 4), round(r["floor_z"], 4)]


def window_cam(name, dist, dx=0.0, dz=0.0, lens=50, tx=0.0, tz=0.0, back=0.0):
    """(loc, target, lens) for a camera `dist` metres out from a room's window (looking +y), aimed at the window
    centre moved by (tx, tz); `back` > 0 puts it inside the room behind the figure instead (looking -y)."""
    r = room(name)
    x, z = r["win_x"], r["win_z"]
    if back:
        return [[x + dx, r["front_y"] + WALL + back, z + dz], [x + tx, r["front_y"] - 1.0, z + tz], lens]
    return [[x + dx, r["front_y"] - dist, z + dz], [x + tx, r["front_y"] + 0.05, z + tz], lens]
