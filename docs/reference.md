# The owner's blocky reference: "In this town touching the ground is forbidden" (2026-10-29)

The owner sent this Short in the `/blocky` session ("Use the same character style", "You can use this as an example") and asked whether we could clone its voice. It's reference reel #10 in `reference_reels_2026-10-29.md`. The video is someone else's, so it isn't committed. This file holds what we measured and what we take from it.

## Measured

| | |
|---|---|
| Length | 136.5 s, 480 x 854, 30 fps |
| Narration | 649 words (faster-whisper `small.en`), **286 wpm** over the whole film, **320 wpm** while speaking. That's about 1.8x a normal audiobook pace |
| Voice | median pitch about 200 Hz, 5th to 95th percentile 123 to 421 Hz (a wide, excited swing), bright (spectral centroid about 2.5 kHz with the music under it) |
| Telling | first person ("My mom and I moved here on a Tuesday"), one short sentence per beat, 2 to 4 s each |
| Captions | 2 to 4 words, white bold sans with a thin dark outline, key words in CAPS (not coloured), centred at 65 to 72% of the frame height. Cap height about 40 px at 1080 wide, smaller than our 56 px floor |
| Shots | a new shot on nearly every sentence (about 45 shots) |

## The story's shape

1. **The rule** (0 to 15 s): a strange town rule, said flat as if it's normal ("touching the ground is strictly forbidden"), with the details that make it real (planks, ropes, chains on the ankles at night, a statue standing barefoot).
2. **The newcomer breaks it** (15 to 42 s): "Nobody warned us about the rule." Four steps, dead silence, the thing comes up.
3. **The second rule** (42 to 47 s): "If someone falls, nobody goes down for them. Not even family."
4. **Someone breaks the second rule** (47 to 75 s): the town turns on them.
5. **The twist** (100 to 115 s): the plaque on the statue explains the monster's real rule.
6. **The reversal** (115 to 130 s): the people who kept the rule are the ones it takes.
7. **The last line** (130 to 136 s): the new normal, and a sign-off.

What makes it work: the rule comes in the first two seconds, every line adds one concrete picture, and the twist was planted in the first 15 s (the statue).

What we don't copy: the story, the town, the monster or the lines. And our hard rules are stricter than the reference. It has a little girl falling, characters dragged under and "she'd get us all killed". We keep it to suspense and the uncanny: no harm to a child shown or described, and no deaths described.

## The look

- **Characters:** R6-style blocky avatars. A box torso, box arms and legs the same width, and a soft rounded-cylinder head. The faces are flat drawings: big round white eyes with black pupils, thin brows and a small mouth, often worried or wavy, plus tears when someone cries. There's block or spiky hair, a hat, and patterned shirts (plaid, knit, stripes) with collars.
- **The set** is realistic next to the avatars: brick buildings, wooden walkways and stairs, cobbles, a stone statue, warm windows and torches, night sky, rain, and a little fog down the street.
- **The camera** is always moving: low angles, over-the-shoulder shots, close-ups on faces, crowd shots from above.

We build all of it ourselves in Blender (note 18): our own head mesh, our own drawn faces and our own clothing patterns. We use no game assets, default faces, decals, UI, fonts or name.

## The voice question

The owner asked "Can you clone this voice?" The team's answer is no clone. It's another creator's audio, and it's either a commercial TTS voice or a recording of a real person. We have no rights to either. Copying a channel's signature voice also invites the reused-content and impersonation reviews. The free cloning models that sound good are mostly non-commercial too.

What we do instead is **match its feel** with Kokoro (Apache 2.0). We run a shootout of voices, then sped them up and shift their pitch toward the numbers above (about 280 to 300 wpm, a median of about 200 Hz, bright), and the owner picks the closest by ear.
