# Style v3: the sheet, for the owner's approval

The owner, 2026-11-12: "Can we also have a redesign of our style? I watched a video about roblox shorts with
claude, and the style is essentially exactly the same as ours. We should have unique like hair styles or unique
facial expressions. like still cartoonish but very exaggerated i think is good."

Nothing ships from this. If the owner approves, stories opt in with `"look": {"style": "v3"}`, so every film already
proofed keeps its look. The engine code is a separate draft PR (`claude/style-v3-engine`).

## What's in here

| File | What it shows |
|---|---|
| `lineup-tv.jpg`, `lineup-phone.jpg` | the six v3 characters side by side (TV size and 300 px wide) |
| `before-after-tv.jpg`, `before-after-phone.jpg` | the same six in today's look (top) and in v3 (bottom) |
| `<name>-tv.jpg`, `<name>-phone.jpg` | each character in 6 expressions (TV size; and each still 300 px wide) |
| `faces.png` | all 17 expressions, flat |
| `hair.jpg` | the hair library: 15 styles (and bald, for a mustache to carry) |
| `acting-test.mp4` | the same 5 s acting beat in today's look (left) and v3 (right), keyed identically: calm, a snap to shock, a suspicious glance, then terror. Silent, 24 fps |

## The six (a style, not a recurring cast: no host, every story keeps its own people)

All adults, apart from Jax (17): nothing kid-coded.

| Name | Hair (the silhouette) | Loud feature |
|---|---|---|
| Rocco | a tall quiff rolling forward off the forehead | the quiff is as tall as his face |
| Mara | a cloud of stacked pink cubes, wider than her shoulders | hot pink hair |
| Gus | a ginger buzz with block sideburns | a giant walrus mustache, most of his face wide |
| Dot | a bun as big as her head, on top | big red square glasses |
| Jax | five electric-blue blades with lime tips | the spikes add half his head again |
| Brick | a red block mohawk with a mustard front fin | a tiny head on giant arms |

## What changed, and why

1. **Hair is the silhouette.** A library of 15 bold block styles (quiff, big bun, spikes, bob with a fringe,
   buzz with sideburns, stacked-cube curls, braids, mohawk, flat-top, mullet, puffs, swoop, top knot, curtains,
   shag) plus mustache, beard and glasses. Today's hair is a thin cap on every head; v3 hair stands off the head,
   so a cast reads by outline alone.
2. **A bigger, squarer head.** A rounded block, wider than the torso (about 40% of the height, up from 23%), so the
   face fills more of a phone screen. Today's head is a cylinder close to the stock avatar's; this is the biggest
   single step away from it.
3. **Faces drawn big, flat and exaggerated.** The face is a flat decal on the head's front, so it can be drawn
   large. Each eye squashes and stretches on its own (so faces go lopsided: smug, suspicious), brows are thick bars
   that fly up or knit hard, mouths open wide onto teeth and a tongue. 17 expressions: neutral, shocked, delighted,
   smug, terrified, cry-laughing, suspicious, heartbroken, determined, furious, nervous, disgusted, deadpan, awe,
   scheming, and two eerie ones for a creepy channel: **hollow** (black eyes, a pin of light) and **toowide** (a
   grin nearly ear to ear, packed with teeth, over pinprick pupils). Cartoon accents: tear streams, flying tears,
   sweat drops, gloom lines, tremble marks. No blush, sparkles, star or heart eyes: both critics read those as
   kid-app stickers (hard rule 3), so they're out. **No shading on faces** (PurpleHat's shaded close-ups were called
   "creepy"): every face pixel is one flat colour, and the face material is matte so the ink never washes out.
4. **A snap on each new face.** When the expression changes, the eyes and brows stretch 15% past the pose in two
   frames and ease back over a quarter second, so the key line lands and holds (`faces_v3.pop_at`). Today the
   face just swaps.
5. **An ink outline** round every part (an inverted hull, drawn for the camera only, no shadows or reflections).
   With the matching ink in the faces, it gives the whole frame one drawn line: our signature.
6. **Chunky mitt hands** and, per character, `head_scale` and `arm_scale` for one loud proportion (Brick).
7. **A louder palette**: tangerine, hot pink, teal, mustard, grape, electric blue and lime, on a range of skin tones.

The body stays the same shape (owner, 2026-11-01: "the same body type"); the head, hair, hands, faces and line
are what move it away from the stock look. Everything is boxes and drawings made in `blocky/`: nothing from any
game's or channel's avatars, faces or assets.

## Render-time cost

Measured here on the same 4-core CPU, Cycles, same lights and samples:

- **Faces cost nothing.** They're flat textures drawn in PIL and cached like v2's.
- **The acting test** (a medium close-up, 120 frames): v2 4.05 s a frame, v3 5.60 s, so **+38%**.
- **The outline alone** is about **+14%** of that (12.4 s against 14.1 s on a 1080 close-up, outline off and on).
  The rest is the bigger head and hair covering more of the frame.
- **Per film, estimated +15 to 35%** on the final draw. Wide shots of a set cost much less than this close-up,
  and close-ups cost the full amount. On the 16 render shards that's minutes, not hours, and it's still $0.
  If it ever matters, `"outline": 0` on a character takes off the outline's share, and the outline can be thinner.

Not measured: a whole real story in v3. That waits for the engine PR and the owner's approval.

## The critics (two fresh reviews, then one revision)

- **Phone scroller, round 1: "Stands out: yes."** Clearly stops the thumb more than today's look; most expressions
  read in one glance. Asked to cut the blush, sparkle, heart and star stickers (kid-app), and flagged that smug,
  deadpan and scheming blurred together, Gus's mustache hid his mouth, and Rocco and Brick both had a dark flat
  block on top.
- **Against the stock avatar look, round 1: "Stands out: not yet."** The big head, the ink line and the faces
  carry it and nothing is copied, but some hair styles were still thin caps, the sticker accents are generic anime
  vocabulary and kid-coded, and a creepy channel needs eerie faces.
- **The revision (one round):** stickers removed; hollow and toowide added; smug (one brow flies up), deadpan
  (flat lids, pin pupils) and scheming (knitted brows, toothy grin) pulled apart; Gus's mustache rebuilt as a walrus
  bar between eyes and mouth; Brick in a red mohawk (a block beard read as a neck brace on his tiny head); the bob, curtains and flat-top given real volume.
- **Round 2: both "Stands out: yes."** The phone scroller now tells all six apart by hair alone, reads the faces as
  teen and up, and finds hollow and toowide "creepy in the good way". The stock-look reviewer says five of six read
  as an ownable look in one frame.
- **Left open for the owner or the engine PR** (not fixed here, as the brief allows one revision): Gus's mustache
  still crowds his open mouths; Dot's glasses crowd her eyes and her disgusted face is weak; nervous is close to
  neutral at 300 px; Brick's small head reads closest to the stock look (his tiny head is his one loud feature, so
  that's a call for the owner); a few library styles (buzz, top knot, curtains) are still slim next to the rest.

About the acting test: both sides use the same camera; the v3 head is bigger, which is the change.
