"""Shared places for ep123 (make_story.py and set.py). x east, y north, z up. A character facing -y has yaw 0.
One porch, one card table. Mae is 13 cm tall and stands on the cloth; the camera comes down to her."""
T = 0.76                      # the cloth's top
MAE = (0.43, -0.36)            # Aunt Mae's feet on the cloth, facing the lens (-y)
MAE_H = 0.13                  # her height in metres (5 in; the tag says 5)
MUG = (0.30, -0.27)           # the mug beside her (a head taller than her)
MUG_H = 0.17
MAE_EYE = 1.57 * (MAE_H / 1.75)   # head centre above her feet
CHAIR = (0.0, 0.98)           # my chair; I sit facing -y
ME_HEAD = (0.0, CHAIR[1], 1.5)    # my head's centre when seated
FAN = (0.0, -0.20)            # Mae's cards lie in a fan at her feet, in front of her
MINE = (-0.02, 0.62)          # my cards on the cloth in front of me
PAD = (-0.30, 0.28)           # the score pad
CAL = (-0.55, 2.55)           # the wall calendar's centre (xy); z 1.25
NEIGH = (0.50, 4.6)           # the neighbor on the lawn behind the porch glass
