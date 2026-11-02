import importlib.util, math, sys
from pathlib import Path
sys.path.insert(0, "/home/user/blocky-stories")
import bpy
from mathutils import Vector as V
import bpy
from blocky import kit
spec = importlib.util.spec_from_file_location("s", "/home/user/blocky-stories/stories/ep58-swing-bridge/set.py")
S = importlib.util.module_from_spec(spec); spec.loader.exec_module(S)
which = sys.argv[-2]; out = sys.argv[-1]
W = Path("/tmp/claude-0/-home-user-blocky-stories/53a68e57-9383-57ac-b3ae-01dbccee7405/scratchpad/faces"); W.mkdir(exist_ok=True)
FOG = "#aeb9c1"
kit.reset()
kit.set_fog(FOG, 0.014 if which == "a" else 0.05, 4.0)
kit.world(FOG, 1.0)
kit.setup_render((540, 960), 48, 4, -0.2)
L = 20.0
if which == "a":
    L = 15.0
    kit.world(FOG, 1.0)
    kit.box("river", (200, 200, 0.1), (0, 0, -1.2), kit.plastic("#435766", 0.4))
    S.bridge(kit, L, rail_y=0.0, origin=(0.5, 0))
    ch = S.make_reach(kit, W, (-0.35, 0.0, 0.0), yaw=math.radians(88), lean=0.0, head_pitch=0.1,
                      rail_pts=[(0.6, -0.12, 1.2), (0.6, 0.12, 1.2)], hands=[(L, -0.12, 1.2), (L, 0.12, 1.2)])
    kit.light("key", "AREA", (8, 6, 6), 900, "#c9d6e2", size=6); kit.aim(kit.LIGHTS["key"]["obj"], (4, 0, 1))
    kit.place_camera((L + 4.5, -2.0, 0.95), (3.0, 2.0, 1.45), 21, 0.0)
else:
    # cabin wall plane y=0, interior y<0; window x -0.6..0.6, z 0.45..2.1
    brick = kit.plastic("#8a4b3a", 0.85); cream = kit.plastic("#d9cfb8", 0.6)
    kit.box("wallL", (4, 0.4, 3), (-2.6, 0, 1.5), brick); kit.box("wallR", (4, 0.4, 3), (3.8, 0, 1.5), brick)
    kit.box("wallB", (2.4, 0.4, 0.45), (0.6, 0, 0.225), brick); kit.box("wallT", (2.4, 0.4, 0.9), (0.6, 0, 2.55), brick)
    kit.box("sill", (2.6, 0.3, 0.06), (0.6, 0.02, 0.47), cream)
    for xx in (-0.62, 1.82): kit.box(f"jamb{xx}", (0.06, 0.3, 1.7), (xx, 0, 1.3), cream)
    kit.box("sashbar", (2.4, 0.05, 0.05), (0.6, -0.02, 2.0), cream)
    kit.box("floor", (10, 6, 0.1), (0, -3, -0.05), kit.plastic("#4a3a2c", 0.8))
    kit.box("wallBack", (10, 0.2, 3), (0, -4.5, 1.5), kit.plastic("#b9a98c", 0.9))
    kit.box("deck", (30, 6, 0.12), (8, 3.5, -0.06), kit.plastic("#7a6a58", 0.9))
    dv = V((0.85, 0.53, 0)).normalized(); pv = V((-dv.y, dv.x, 0)); o = V((-0.1, 1.9, 1.2))
    S.bridge(kit, 22, rail_y=0.0, origin=(o.x, o.y), dirv=(dv.x, dv.y))
    ch = S.make_reach(kit, W, (0.05, 0.85, 0.0), yaw=0.0, lean=0.5, head_pitch=-0.5,
                      rail_pts=[o + dv * 0.2 + pv * s_ * 0.13 for s_ in (-1, 1)],
                      hands=[o + dv * 19 + pv * s_ * 0.13 for s_ in (-1, 1)])
    kit.light("lamp", "POINT", (-0.9, -1.2, 1.3), 32, "#f0a24a", size=0.2)
    kit.light("ember", "POINT", (0.4, -0.8, 0.3), 6, "#e0682a", size=0.2)
    kit.light("rim", "AREA", (1.5, 6, 3), 500, "#8fb0d0", size=4); kit.aim(kit.LIGHTS["rim"]["obj"], (0, 0.6, 1.4))
    kit.place_camera((0.0, -2.1, 1.4), (0.35, 1.5, 1.4), 22)
kit.update_lights(0)
kit.render_to(out)
