# Creature round 2: Hal (ep87) and the Server (ep71), 2026-11-03

This round tested the creature lab's two best revival bets (`creature-playbook.md` → "Which dropped stories look
revivable") against the playbook's pass zone (rules 12 to 15). Each creature got two tries, each by a fresh Sonnet
`builder`, rendered through the story's real set with `look.polish` on. Each try was judged by **two** fresh Opus
critics, who saw only the script's creature description, the channel look and the still at 390 px wide. To pass,
a try needed both critics to say frightening and score 7 or more.

**Result: neither passes.** Hal's best was 5 and 4; the Server's best was 4 and 4. No revival branch was made.

## Hal (ep87-motel-rooms)

| Try | Scores | Reads | Critic A's why | Critic B's why |
|---|---|---|---|---|
| 1 | 4, 3 | silly, silly | "a tall orange robot or mannequin with a stick neck": one flat warm orange, tiny head on a pole neck "tilted like a curious toy", dark space above the head so no stoop | "a lamp behind a counter wearing brown suspenders": no ceiling over his head, the warm light reads friendly, the lapels read as suspenders |
| 2 | 5, 4 | frightening (only just), silly | "a friendly yellow-blazer clerk with glowing eyes": the eyes and tipped head are eerie, but the ceiling fades into dark and the narrator is cropped, so he reads as normal height | "a bright-yellow bellhop with glowing eyes": no ceiling touching him, the mustard blazer and flat mouth read goofy, "the glowing eyes are the only eerie part" |

Stills: `creature-lab/hal-r2-t1.jpg`, `creature-lab/hal-r2-t2.jpg`.

What moved: square, unblinking emitter eyes under a shadowed brow (rule 15) were the first thing any critic called
eerie, in both try-2 reads. What never landed, in all four reads: **the scale proof.** Both builders were told the
head must press into a ceiling beam with no dark gap above it, and in both stills there's still a dark band above
the head and the narrator is cropped at the edge. The mustard blazer reads as cheerful in every read, even
darkened to `#8a6a1e`.

Try 2's design, the closest yet, for anyone who tries again (in `set.py` `hal(kit,P,B,th)`, metres, x right, y away
from camera, z up):
- Hal: hip at (0, 1.8, 0.88), torso pitched 10° toward the camera; torso 0.34 x 0.2 x 1.1 `#8a6a1e`; shoulder bar
  0.44 x 0.22 x 0.12; neck 0.1 cube; head 0.25 x 0.25 x 0.26, pitched 30° forward and rolled 15°, about 1.3 above
  the hip; brow 0.26 x 0.05 x 0.05; eyes two emissive 2.8 cm squares `#eaf6ff` at strength 60, x ±0.065; mouth a
  0.11 dark line; shirt V, dark tie `#221018`, lapels and notches `#5a430f`, a brass name bar; cuffs at
  (±0.3, 0.66, 1.1) with four fingers each draped over the desk front; the bell at (0, 0.62, 1.1).
- Ceiling slab 6.2 x 0.7 x 0.2 at (0, 1.7, 2.36).
- Lights: an under-key SPOT at (0, 0.3, 1.08), 90 W, `#bcdcff`, 42°, aimed at (0, 1.8, 1.75); a beam SPOT at
  (-0.4, 0.8, 1.5), 35 W; the pink neon rim SPOT from behind (from try 1: (0.95, 3.15, 2.3), 3500 W, `#ff3fa8`).
- Camera (0, -3.0, 1.0) looking at (0.1, 1.8, 1.85), lens 54; the narrator at (-0.5, 0.2), yaw 70.

If Hal gets a third try, the only change that matters is the one never achieved: his head physically bent
against a **lit** ceiling beam inside the frame, the narrator's whole head in frame at Hal's chest, and a dingy
blazer (not mustard yellow).

## The Server (ep71-two-windows)

| Try | Scores | Reads | Critic A's why | Critic B's why |
|---|---|---|---|---|
| 1 | 4, 4 | silly, silly | "a tilted brown box or grill-faced robot with a peach lid": the dark, cocked head is no wider than the shoulders, so the one wrong thing never shows; dot eyes and peg teeth "look like a toy or a toaster" | "a dark tilted box or grill with buck teeth": the tiny eyes vanish, the toothy mouth looks goofy, the head isn't clearly wider than the hatch |
| 2 | 3, 3 | silly, silly | "a wall air-conditioner or a cardboard box sitting on a mint shirt": a smooth beige slab with dot eyes and a line mouth reads as "a prop or a meme face", the body hidden behind Cal | "a beige wall air-conditioner or cardboard box": the flat slab, dot eyes, line mouth and visor brim "look like a vent lid", evenly lit |

Stills: `creature-lab/server-r2-t1.jpg`, `creature-lab/server-r2-t2.jpg`.

Try 1 followed r2-critic's fixes (tilted head, uneven jaw, three uneven teeth, glint eyes); try 2 followed try 1's
critics (a level, skin-toned slab spanning the hatch, flat mouth). Both read as an object. Across four rounds now
the Server has read as "a TV or toaster", "a grey box with a comb grin", "a grill" and "an air-conditioner".

## What this round shows

1. **A head defined as a wide slab is an appliance outline** (playbook rule 1). Dark or light, tilted or level,
   toothed or flat, it reads as a box at 390 px. The Server needs a writer change to its concept, not another
   design try: for example, a normal head on a neck stretched sideways across the hatch, or a face that fills the
   hatch from inside with nothing around it. That's a writer call.
2. **Eyes: the critics disagree with rule 15.** Five of the eight reads asked for bigger, brighter eyes, three
   for "whites with pinpoint pupils". The lab's Hal try-2 critic called that "googly-eyed". Small square
   emitters under a shadowed brow were the only eyes called eerie. Keep rule 15, but the glints must be larger
   than about 1.5 cm: 2.8 cm read, 1.5 cm vanished.
3. **Builders don't land the scale shot from a written brief.** Both Hal tries were told "head against the
   ceiling, narrator's whole head in frame", and both missed. A third try should check the still for those two
   facts before it reports, and fail itself if they're missing.
4. Hal remains revivable at best with a third try. Neither story should go to a build session on this evidence.
