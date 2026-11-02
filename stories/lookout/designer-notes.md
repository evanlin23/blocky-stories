# ep14-lookout: designer notes (motion-designer)

> **Superseded in part (2026-11-02, redo 2).** The story is now rule first with no creature (see `script.md` → "BUILDER: what changes and what's reused"). Everything below about the giant is retired. The notes on the tower, cab, lamp, fog and pines still hold.


## Creature test still

### Pass 2 (critic round 1: revise, scary 4, silly 4)

**The stills:**
- **Fear:** `review/creature-test.png` (+ `creature-test-small.png`), the L42 to L44 beat, caption "an ARM'S LENGTH".
  - My terrified face, lamp-lit tan and turned back over my shoulder with my eyes still sliding to it, fills the lower-left below the captions.
  - Over me, the giant's head is one near-black faceted mass, its broken rim against the night fog.
  - Two warm lights sit in the hollow's dark, and the near one is half behind the lip, so it peers.
- **Scale:** `review/creature-scale.png` (+ `creature-scale-small.png`), the 03 fog top (L30), caption "something TALLER". In daytime pearl fog it shows:
  - the giant walking up the ridge toward the tower, seen from behind (no face yet)
  - its log chest, both stone humps and its stump above the fog and the pine tops, the pines reaching its chest
  - the tower beside it at the same distance as the ruler, with me a speck on the catwalk
  - It reads from the silhouette alone.
- Both are 540 x 960 drawn at 16 samples (24 s and 39 s), finished by `stills`. Every probe is in the scratchpad (`iter/q*`, `iter/s*`, `iter/final2-*`).

**What changed, item by item:**
1. **Fear still from the deck.**
   - The camera is 1.3 m behind my right shoulder, just inside the cab glass (the catwalk is only 1 m deep), on a 15 mm lens.
   - My body is twisted 57 degrees away to my right and my head turned 56 degrees back toward the lens, with my eyes held on it (`look` 0.95). Behind the shoulder a profile can't show, because the hood frames the face.
   - The lamp hangs from my right hand.
   - The giant's head is turned 12 degrees, so the lens is 27 degrees off the hollow's axis and the near light sits half behind the front wall's inner edge.
   - Its lights moved up into the hollow's upper part (0.6 m above its middle, 21.4 m in this pose, 21.5 standing).
   - I placed it all with a small projector and search (`scratchpad/proj.py`, `search.py`, `refine.py`) before rendering.
2. **Silhouette, not lit object.**
   - My lamp's throw is 60 W and lights only the stump and limbs, never the stones or saplings. The lantern's own light skips the stones too.
   - The night fill never reaches the giant (or me). The rim is a low spot behind it (60,000 W at (3, -30, 21), 26 degree cone) that grazes edges instead of lighting tops.
   - The hollow's walls are #22170e and kept out of the fog, with 14 W of glow per light, so they're warm only right round the lights.
   - Measured on the fear still: the giant's mass averages luma 4.6 against a sky of about 89.
   - The stray black sliver was the torso's core box. It wore the fog-free hollow material, so it showed pitch black through the fog. It now has a fogged dark matte. A check render from pass 1's 3/4 angle shows no sliver, dark stones and a thin rim (`iter/check34-big.png`).
3. **A second still for scale:** the daytime fog top above.
   - It needed a day look in the same story, so `set.py` now has a `look` cue (`LOOKS`: night and day) that retints every kit-fogged material's fog colour and density. It also sets the sky, exposure, suns and light gains, and which fog cards show (six at most per look).
   - Day: fog #b8bcb8 at 0.0045 per metre from 20 m, the sky's ambient halved (0.45) so the giant darkens against the bright fog cards, and a soft sun (1.1) low behind it.
4. **Block world (note 21).**
   - Every log is now a square bevelled timber, with flat end grain at 45 to 68% of #6e5a44 and a solid moss top on every flat upward face. That's the torso's log-cabin courses of 0.92 m timbers, the limbs' four 2.2 m square posts, and the toes as tapered square timbers.
   - The bark is a flat colour with long streaks and dirt (`block_bark_mat`), with no sculpted plates. That's the critic's crumpled foil gone.
   - The stump is 14 flat facets with a calmer broken rim.
   - The shoulder stones are faceted block boulders (an icosphere with 80 flat facets, corners pushed in or out) with moss on their up-facing facets.
   - The narrator and the giant are now the same kind of thing: boxes, bevels and flat colours.

**Two fixes the critic's notes led to:**
- **The narrator's hood hid the face.** `rig.py` builds the hood as a closed box whose front face sits 1 cm in front of the drawn face, despite its own comment ("open at the front"). So any hooded character has no face, which is why pass 1 read as a dark cube or crates. I didn't touch `rig.py`. `set.py`'s `open_hood()` rebuilds this story's hood once on the first frame, open at the front and the neck, 0.12 units thick with a bevel. No other story uses a hood. **The engine fix should still happen in `rig.py`** (opt-in or not, since no story uses the hood yet). That's the producer's call.
- **My face key.** My raised arm sits between the hanging lantern and my face, so a 12 W warm key from below and in front of my face, lighting only me, does the lantern's work. It's placed from my head each frame and is off in the day look.

**Measured:**
- **Fear brightness:** the far light peaks at luma 254 (core 255/255/240) and the half-hidden near light at 207. The lantern is 195, my face 142 at most (no clipping) and the sky 89.
- **Fear frame:** my face is in the lower-left (x 0 to 0.37, y 0.75 to 0.98), clear of the caption block. The lights are at y 0.45 to 0.5, above the caption band. The hollow is about 0.69 of the frame width.
- **Contact probe** (BVH, both poses, `scratchpad/dbg/contact.py`, now with the pines): no overlaps with the tower, me or any pine.
  - Fear pose: the nearest tower point is a root toe 0.22 m from the south-east leg's foot. The hollow's lip is 1.41 m from me, and the nearest pine 2.25 m.
  - Scale pose: the tower is 7.3 m away, the nearest pine 3.9 m.
  - The giant's clear zones are now 13.5 and 15 m, because a pine's lowest branches reach 4 m and its arms 9.2.
- **Tests and checks:** unchanged from pass 1. `check` and `test_every_story_passes_its_checks[lookout]` block only on the placeholder's 5.3 s length, and the other 37 tests pass.

**Departures, for the critic and producer:**
- **The fear camera tilts about 10 degrees down, not up.** With its lights at my eye height, any up-tilt from behind my shoulder put my face in the caption band or on the near light. I kept the framing goals (face lower-left under the captions, lights above them, the hollow over half the width, the peer) and gave up the tilt. It still looms, because its rim fills the top of frame over my head.
- **The lights sit 0.6 m higher in the hollow** than the brief's 20.9 m standing (21.5 m). They're still level with the cab window.
- **The fear pose moved** to put the hollow's lip 1.4 m from me. The 3/4 from pass 1 is kept in the generator as `REVEAL_34` for L45's cutaway, and the window close as `WINDOW_CLOSE`.
- **The scale wide is from far down the ridge** (about 95 m) on a 38 mm lens, with no pines in the first 55 m so nothing blocks the lens.

**Honest scores:**
- **Fear still:** scary 6, silly 2. Its proximity and the peering light work, and my face sells it. It's a classic creature-feature beat rather than a new image, and the cartoon face style softens it a little.
- **Scale still:** scale 8, scary 4, silly 3. It reads as a giant figure walking up to my tower. Some viewers may still see a blocky statue until it moves.

### Pass 1 (kept for the record)

Pass 1's still was the 3/4 from past the west rail. The critic read it as a haunted stump with lit windows next to a hut: no figure, no scale, and the narrator as crates. Its story in short (34 probes):
- **Rejected framings:** the window close was a cartoon ghost mask, and the far wide put a tower-sized barrel beside the tower.
- **Bark and rim:** regular ridges read as barrel staves and battlements.
- **Lighting bugs:**
  - a stale-transform key at the world origin
  - a key lighting the hollow like a room
  - a bump steep enough to turn the bark black
- **Hollow shape:** an underlit lower lip read as a jaw, then a smile, until a toe board flagged it. A round-topped opening read as a fairy house until it became an almond split.
- **Contact:** a toe collision with the tower's leg.
- **What carried into pass 2:** the ember lights, the almond hollow, the shadow-only curtain in the mouth, the toe board and the build-time check on the boolean.

**Pass 1's design and lights** (superseded where pass 2 says so above; `set.py`'s `build_giant()` builds the giant once and `pose_giant()` only moves it):
- **Body plan:** R6 at 13.5 times my 1.75 m. The legs are 4.6 x 4.6 x 9.2 m (hips at 9.2), the torso 9.2 x 4.6 x 9.2 m (top at 18.4), the arms 4.6 x 4.6 x 9.2 m (centres 6.9 m out, shoulder pivot at 17.25), so it's 18.4 m across the arms. The head's base is at 18.4 and its rim at 23.4 to 23.9, so it stands about 23.6 m. Standing, the lights are at 20.9 m. In the scare lean they're at 20.74.
- **Torso:** a log-cabin wall of 0.92 m round logs, ten courses on the front and back, side courses offset half a log, crossed ends 0.5 m out at every corner, two mossy logs across the top, and a dark core box so no daylight shows between courses.
- **Limbs:** bundles of four upright logs about 2.2 m thick each. Four logs filling a 4.6 m square can't be 0.9 m thick, so the brief's 0.9 m applies to the torso only. Each foot has four root toes at the front, 1 m thick (tapering) and 1.5 to 1.7 m long.
- **Head:** a hollow stump 5 m across (flared to about 5.4 at its base), 5 m to a broken rim that slopes 0.5 m from its high right-back to its low left-front, with two broad splinters (0.3 and 0.2 m) and a notch where the split reaches the rim. It's a thick-walled shell (0.55 m walls) round a cavity 3.8 m across and 3.6 m tall, with a sunken mossy cap 0.5 m below the rim.
- **Hollow:** an almond split 2.5 m wide and 3.3 m tall (the brief's "about 2.8 x 3"), centred 2.5 m above the head's base, ragged on its upper half and worn smooth below, with a narrow split on up to the rim. It's at least 2 m deep (3.8 m to the back wall).
- **Lights:** two spheres 0.35 m across, 1.2 m apart, 1.5 m inside the mouth.
  - The ember shader has a core #ffcf94 fading to #ff8a2c at the rim, emission 0.8, transparent at the edge.
  - Each has a point light inside (#ffb860, 45 W, 0.17 m soft) that warms the hollow's walls (#3a2818, out of the distance fog).
  - They swell 15% and back over 10 s (5 s up). They never blink, flicker or change colour.
- **Shoulders:** boulders 3.9 m (its left) and 3.6 m (its right) across, #7e8378 with dark mottling, lichen bump and moss caps, sunk into the torso's top corners so their tops reach the middle of the head. Three pine saplings (1.1 to 1.45 m) on its left stone and one (1.2 m) on its right. They're the same pine mesh as every forest tree.
- **Colours:**
  - bark #3b2a1e in plates (0.6 to 1.35 times the colour) split by cracks at 0.08 times it, with dirt patches
  - log ends #6e5a44, drawn at 50 to 72% of it with dirt so they're never pale
  - moss #3b4f1e to #5f7a2e, darkened 30%, on every face whose normal points up, plus a patchy spill just under the rim
- **Never:** no mouth, nose, carving, smile, antlers, rods, tentacles or clothes, and nothing thin.

**The night look in the still:**
- **Fog and exposure:** fog #2a3238 at 0.034 per metre from 3 m, sky #2a3238, exposure 1.6.
- **Lights:**
  - the lantern's flame (95 W, #ffd9a0, soft 0.2, lighting everything but the lantern's own frame)
  - the lamp's throw on the giant (`lampkey`, 1500 W point at the lantern, #ffd9a0, linked to the giant only)
  - a cold fill (sun 1.5, #8ea6c4, 24 degrees up from the east-south-east, so the side the camera sees falls dark)
  - a cold rim (spot 110,000 W, #a9c0d8, at (-12, -27, 25) behind it, 30 degree cone, giant only)
- **Grade:** shadows [-0.02, 0.01, 0.02], highlights [0.04, 0.015, -0.03], saturation 0.9, contrast 1.08, vignette 0.35, bloom 0.45, grain 0.014, `red_line` 0.79.
- **Caption key colour:** amber #ffb22e. Checked on this lamp-in-fog frame, it reads cleanly on the blue-grey fog and matches the lights. I don't see a need for the river-blue fallback.

**Where the still departs from the brief, and why** (for the producer and standards):
- **The key isn't "behind me through the cab glass".**
  - From inside the cab, a lamp behind me is within about 15 degrees of frontal for a face that's looking at the cab. That flattened the bark and made it toy-like (p13). The cab's lower wall also blocks a lamp on its floor.
  - In the scare I've set the lamp down on the catwalk at my right foot. The toe board flags it, so it's a key from below that rakes up the face.
  - Two cheats help: a second light at the lantern does the long throw and lights only the giant, and the shadow-only curtain keeps it out of the hollow.
- **"An arm's length" is 1.2 m.**
  - The mouth can't come closer without the head crossing the rail, and the brief's foot-clearance rule is 1 m.
  - With the brief's sizes, a stone shoulder can't rest on the tower frame while the hollow faces me at the south rail. The stones sit 4.2 m out from the head's middle, at its depth, about 4 to 5 m from the tower.
  - For the lean beat I'd turn its body about 30 degrees so its right stone meets the catwalk's south-east corner (it comes within about 2 m at yaw 210), with the head turned back to me. That needs its own contact probe.
- **The cab has one wide pane a side**, glass from 0.5 to 2.9 m (eave at 3.1). A mullion through the face at the glass was the problem in p4.
- **The still isn't the brief's catwalk close** (hollow at least half the frame width). That close is kept in the generator as `WINDOW_CLOSE` (the south window from inside the cab). It's creepy but has no scale (p14 to p18). I'd cut the reveal as that close for the lights rising, on ones, then this 3/4 for "stone shoulders after them".
- **The road low wide** (the brief's second test still) isn't made yet.

**Housekeeping:**
- The story folder is minimal for the still. `generator/lines.json` has two placeholder narrator lines from the brief (voice A, voiced). The generator has two shots and one giant cue.
- Until the scriptwriter's script replaces the placeholder, `python -m reels.blocky check lookout` blocks on length (5.3 s) and `test_every_story_passes_its_checks[lookout]` fails for the same reason. The other 37 blocky tests pass.
- No engine file changed (`kit.py`, `rig.py`, `post.py`, `sound.py`, `faces.py`, `timeline.py`, `checks.py`).
- `set.py` checks its own boolean at build and prints a warning if the hollow's cut ever eats the shell. It happened twice while iterating, both times from a self-intersecting outline or profile.

**What the full set adds:**
- **The cab:**
  - the cot (built), binoculars, a log sheet with ruled lines only
  - the radio, a plain black box with one green light that glows while she transmits
  - the lamp's bail in my hand, placed each frame by `set.py`
  - a faint daytime reflection on the glass (night stays reflection-free)
- **The tower:** switchback plank stairs (112 steps of 0.175 m if the script keeps the line) and the plank gate at the foot. The legs and braces are built.
- **The forest:**
  - instanced pines 14 to 17 m (linked duplicates of the one pine mesh) with gold larch patches #c8962e
  - snapped pines on the far ridge
  - the smoke smudge #7a6e62 that later lies in the valley
  - up to six fog cards in all
- **The foot of the tower:** mud, needles, gold leaves and the prints (a 4.6 m square heel and four toe grooves, dark rough water that reflects nobody).
- **The fire road and valley edge:** the rutted track, the rocky shelf, the valley smoke and the thin silver river (emit). Spring, green and fogless, gets a sapling in every print.
- **The giant's acting:**
  - a stiff R6 walk from the hip with footfalls on the pulse
  - pines it passes leaning apart and springing back
  - head turns of 60 degrees at most, and the lean onto the frame in the scare
  - each beat probed for contact before the final
- **Looks:** per-shot looks (a `shot` cue as in closing-time), pearl fog by day (#b8bcb8), and first light.
