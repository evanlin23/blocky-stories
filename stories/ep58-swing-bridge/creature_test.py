"""Creature test stills (run with the bpy python: creature_test.py a|b OUT.png)."""
import importlib.util, math, sys
from pathlib import Path
sys.path.insert(0, "/home/user/blocky-stories")
import bpy
from mathutils import Vector as V
from blocky import kit
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("s", HERE / "set.py")
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
which, out = sys.argv[-2], sys.argv[-1]
W = Path("/home/user/blocky-stories/out/ep58-swing-bridge/faces"); W.mkdir(parents=True, exist_ok=True)
NIGHT, FOGC = "#1a2a4a", "#18233d"
kit.reset()
kit.set_fog(FOGC, 0.03 if which == "a" else 0.05, 3.0)
kit.world(NIGHT, 1.6)
kit.setup_render((540, 960), 48, 4, -0.4 if which == "a" else -0.8)
def moon(loc, tgt, e=600, c="#7f9fd0"):
    kit.light("moon", "AREA", loc, e, c, size=6); kit.aim(kit.LIGHTS["moon"]["obj"], tgt)
if which == "a":
    L = 9.0
    kit.box("river", (200, 200, 0.1), (0, 0, -1.2), kit.plastic("#223348", 0.95))
    kit.box("bank", (6, 8, 0.2), (-3.5, 0, -0.1), kit.plastic("#2a2a24", 0.9))
    S.bridge(kit, L, rail_y=0.0, origin=(0.0, 0))
    z = 1.12
    def paths(sl, sr):
        k = 0.22   # arms a hand's width apart, with a slight elbow bend partway
        return [[sl, V((0.5, -0.3, 1.0)), V((1.2, -0.12, z)), V((4.0, -0.12, z)), V((4.4, -0.2, z)), V((L, -0.12, z))],
                [sr, V((0.5, 0.3, 1.0)), V((1.2, 0.12, z)), V((4.0, 0.12, z)), V((4.4, 0.2, z)), V((L, 0.12, z))]]
    S.make_reach(kit, W, (-0.55, 0.0, 0.0), yaw=math.radians(90), head_pitch=0.1, paths=paths)
    kit.light("lamp", "POINT", (-0.3, -1.0, 0.15), 120, "#f0a24a", size=0.15)
    moon((6, 8, 7), (5, 0, 1), 1500)
    kit.light("fill", "AREA", (L + 3, -7, 5), 1600, "#9db8e0", size=6); kit.aim(kit.LIGHTS["fill"]["obj"], (4, 0, 1))
    kit.place_camera((L + 6.0, -2.6, 0.95), (3.5, 0.8, 1.3), 36)
else:
    brick = kit.plastic("#7a4535", 0.85); cream = kit.plastic("#cfc5ae", 0.6)
    kit.box("wallL", (4, 0.4, 3), (-2.6, 0, 1.5), brick); kit.box("wallR", (4, 0.4, 3), (4.4, 0, 1.5), brick)
    kit.box("wallB", (3.0, 0.4, 0.45), (0.9, 0, 0.225), brick); kit.box("wallT", (3.0, 0.4, 0.9), (0.9, 0, 2.55), brick)
    kit.box("sill", (3.0, 0.5, 0.06), (0.9, 0.0, 0.47), cream)
    kit.box("floor", (12, 8, 0.1), (0, -4, -0.05), kit.plastic("#3a2c20", 0.8))
    kit.box("wallBack", (12, 0.2, 3), (0, -6, 1.5), kit.plastic("#5a4c3c", 0.9))
    kit.box("deck", (30, 6, 0.12), (8, 3.5, -0.06), kit.plastic("#5a5a5a", 0.9))
    dv = V((0.95, 0.3, 0)).normalized(); pv = V((-dv.y, dv.x, 0)); o = V((1.1, 1.8, 1.12))
    S.bridge(kit, 24, rail_y=0.0, origin=(o.x, o.y), dirv=(dv.x, dv.y))
    sillz = 0.47 + 0.03 + 0.1
    def paths(sl, sr):
        # sl: shoulder nearer the camera (-x): drops through the open window and lies along the sill, hand at the camera
        a = [sl, V((sl.x - 0.05, 0.1, sillz + 0.2)), V((0.05, 0.0, sillz)), V((-0.3, -0.1, sillz))]
        b = [sr, V((sr.x + 0.3, 1.1, 1.15)), o + dv * 0.3 + pv * 0.12, o + dv * 7 + pv * 0.12, o + dv * 7.4 + pv * 0.2, o + dv * 23 + pv * 0.12]
        return [a, b]
    S.make_reach(kit, W, (0.75, 0.95, 0.0), yaw=-0.45, lean=0.5, head_pitch=-0.45, head_yaw=0.0, paths=paths)
    kit.light("sill", "POINT", (0.45, -0.35, 0.62), 14, "#f0a24a", size=0.1)
    moon((3, 8, 4), (1, 1, 1.4), 4000)
    kit.light("fill", "AREA", (3.0, -2.2, 3.0), 350, "#9db8e0", size=3); kit.aim(kit.LIGHTS["fill"]["obj"], (1.0, 1.2, 1.2))
    kit.light("fill2", "POINT", (2.2, -0.3, 1.3), 1000, "#9db8e0", size=0.3)
    kit.place_camera((-1.3, -1.9, 1.05), (0.9, 0.4, 1.15), 22)
kit.update_lights(0)
kit.render_to(out)
