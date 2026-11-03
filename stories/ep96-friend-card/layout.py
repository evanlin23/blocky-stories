"""Where each stage of ep96-friend-card sits in the one Blender scene, and the few places the story keys against.
Shared by set.py and generator/make_story.py. Stages are 100 m apart so no shot sees a neighbour."""
ST = {"roof": (0, 0), "hand": (200, 0), "hall": (300, 0), "park": (400, 0), "lawn": (500, 0), "gate": (600, 0),
      "curb": (700, 0), "cal": (800, 0), "living": (900, 0), "diner": (1000, 0), "porch": (1100, 0),
      "yard": (1200, 0), "garage": (1300, 0), "bowl": (1400, 0), "beach": (1500, 0), "van": (1600, 0),
      "bench": (1700, 0), "street": (1800, 0), "win": (1900, 0)}
ARCH_Y = 12.0      # the flower arch on the roof, x = 0
HAND_C = (0.0, 0.0, 1.2)   # the hand rig's centre, relative to the hand stage origin


def P(stage, x=0.0, y=0.0, z=0.0):
    ox, oy = ST[stage]
    return [round(ox + x, 3), round(oy + y, 3), z]
