---
role: standards
round: 3
verdict: approve
score: 9/10
---

# ep13-closing-time · Round 3 · Standards and practices

**Standards, 2026-10-31.** I reviewed the round 3 patch on the final file. I didn't change the stage, the story, the render, `qa.json` or any other file, and I didn't commit. My scratch scripts, outputs and stills are outside the repo, in `/tmp/claude-0/-home-user-content/c2eb1c9d-6fc3-507c-96d9-6463a562d472/scratchpad/stds13r3/`.

**What I reviewed:**
- The final `history-sound/out/ep13-closing-time.mp4`. I hashed it myself: **SHA-256 `c04ce50f139228b5e13e64d557e7aa015308f918e6a764475251549abaf0bd88`**, the same as the designer's. It's 1080x1920, 30 fps, 4041 frames, 134.70 s, H.264 and AAC 48 kHz stereo.
- All 4041 composed frames, built in memory the way `post.encode` builds them, from the drawings in `blocky-work/closing-time/frames`.
- `timeline.json` (69 shots, written 10:06), `generator/lines.json`, `03-reel.md`, `02b-script.md`, `04-decision-r2.md`, the "Round 3 patch" section of `designer-notes.md`, `qa.json`, `status.json` and my round 2 sheet.
- The designer's stills `post-03228`, `03246`, `03270` (S58) and `post-03972`, `03990`, `04008`, `04026`, `04040` (S69). I checked each against the same frame pulled from the mp4.

**This is a compliance review, not legal advice.** Nothing here needs a lawyer. My standing judgement calls from rounds 1 and 2 still hold: the blocky style against the game's look, no AI disclosure for a TTS narrator in a cartoon, and made for kids being the owner's own declaration on a channel with a kid-coded name.

## Verdict: approve, 9/10

R5, R6 and R7 are all closed:
- **R5:** the S58 bow no longer passes through the rail or the glass, and the S59 rise is clean too.
- **R6:** `studio check --final` ran on this file at 10:50 and found 0 blocks and 0 warnings. `qa.json` matches the file: 134.7 s, -14.3 LUFS.
- **R7:** `designer-notes.md` now has the whole-film flash table, and my measurements agree with it.

The new tail adds no flash and no contact problem. The new last line breaks no fiction, brand or word rule. There's no licence issue, no policy problem, and nothing needs fixing before upload.

One point is held back from a 10, and it isn't mine to fix: D1 asked for the pup to be whole and at least 15% in from the left edge. For about the first second of the glide (132.45 to about 133.5 s) it's still coming in from the edge. The designer recorded this as "not met exactly". It's not a compliance issue, so it goes to the critic and the producer.

## Checklist

| # | Item | | Note |
|---|---|---|---|
| 1 | The file's hash | ✓ | `c04ce50f…abaf0bd88`, verified, 4041 frames, 134.70 s |
| 2 | R5, S58 bow against the rail, posts, frame and acrylic | ✓ | Section A: 0 hits on all 31 drawings |
| 3 | R5, the S59 rise (109.33 to 110.0 s) | ✓ | Section A: 0 hits |
| 4 | Contact in the S69 tail (130.8 to 134.7 s) | ✓ | Section B: 0 overlaps, and the pup stays behind the tank face |
| 5 | Stills, S58 and S69, against the mp4 | ✓ | Section C |
| 6 | `house_report`, whole film, mp4 | ✓ | Section D: passes, the same as round 2 |
| 7 | `house_report`, whole film, composed frames | ✓ | Section D: matches the mp4 |
| 8 | The replay seam | ✓ | 0 transitions on every reading. Round 2's small fall is gone |
| 9 | `bound.py` on the mp4 | ✓ | No cut flagged |
| 10 | The redraw list | ✓ | All 96 drawings in `redraw.txt` are newer than `timeline.json`, nothing is missing, and nothing else changed (the only other new file is `render-time.json`) |
| 11 | The flashing-lights span | ✓ | `0:02 to 2:13`, unchanged |
| 12 | L85 against the fiction, brand and banned-word rules | ✓ | Section E |
| 13 | Audio, loudness and synthesis | ✓ | -14.3 LUFS, -2.1 dBTP, LRA 1.7 LU (my own ebur128 reading). Only the new glide sound was added, and it's synthesized |
| 14 | R6, QA up to date | ✓ | `qa.json` at 10:50:40Z, `final: true`, 0 blocks and 0 warnings, on this file |
| 15 | R7, the flash table in `designer-notes.md` | ✓ | Present, and my numbers agree with it |
| 16 | R3, the board title | ⚠ carried | `status.json` still says "Always wave goodbye to the big tank". The packager's title replaces it |
| 17 | D1's "whole and 15% in" | ⚠ not mine | About 1 s short at the start of the glide. Critic and producer |
| 18 | `03-reel.md` header wording | ⚠ cosmetic | It says both "round 3 patch" and "the round 2 patch". Internal only, and `studio voice` passes the on-screen text. Optional fix for the motion-designer |

## A. R5: the S58 bow and the S59 rise (Blender probe)

My new `stds13r3/probe_bow3.py` builds the scene like `bl_story.main` (`acting.state` plus `set.animate`) at **every drawn frame from 3214 to 3300** (107.13 to 110.00 s: the end of S57, all of S58 and the first 0.67 s of S59). Nothing is rendered. At each frame it:
- runs a BVH overlap of every cast mesh against the acrylic, every frame piece, the rail and the seven posts
- measures each cast member's nearest distance to the rail tube and to the acrylic
- records each cast member's lowest y (the hall face of the glass is y = 0)

I also re-ran round 2's `stds13r2/probe_bow.py` (107.3 to 109.3 s in 0.1 s steps). It's clean on all 21 times.

| | S58 (31 drawings) | S59 rise (11 drawings) |
|---|---|---|
| Overlaps with the rail, posts, frame or acrylic | **0** | **0** |
| Closest to the rail tube | Dev 5.6 cm (107.53 s), me 8.3 cm (107.53 s), Rosa 8.4 cm (107.93 s) | Dev 21 cm |
| Closest to the acrylic | Rosa 26.3 cm (108.8 s), Dev 30.6 cm, me 39 cm | Rosa 27.6 cm |
| Past the glass's hall face (y < 0) | none | none |

The only hits in the probed window are at 107.13 and 107.20 s, in **S57**: my forearm and Dev's on the rail, and Rosa's sleeve and forearm on rail post 4. That's the ordinary resting contact I cleared in round 2, before the bow starts. It isn't a body passing through anything.

**R5 is closed.** At 46 degrees, 0.35 m further back, the cast bow over the rail, not through it.

## B. The S69 tail (Blender probe)

I ran `stds13r2/probe13.py` from 130.8 to 134.7 s in 0.05 s steps (79 times: the end of S68, then S69 to the cut).
- **0 overlapping pairs** between any cast member and the Regular or the pup.
- **Closest:** me to the pup at **0.787 m** (132.05 s), me to the Regular at 1.99 m, Dev to the pup at 2.79 m. Rosa isn't in the probe's cast here: she's off screen in the tail and has no visible mesh.
- **The glass:** the pup's highest y is **-0.307 m** and the Regular's is -1.27 m. Both are behind the acrylic's tank face at -0.300 m, so nothing comes through the glass.
- **The cast's lowest y** is 0.339 m (me) and 0.341 m (Dev), both on the hall side.

These match the designer's numbers.

## C. Stills

I pulled frames 3228, 3246, 3270, 3972, 3990, 4008, 4026 and 4040 from the mp4 and compared each with the designer's still. Six match to within encode noise (mean absolute difference 1.5 to 2.3 out of 255). Frames 3990 and 4008 differ by 4.9 and 4.2, and side by side the only difference is where the bubbles are. The creature, the framing and the captions are the same. My pair is at `stds13r3/mp4stills/pair-3990-4008.png`.

- **S58 (107.6, 108.2 and 109.0 s):** the three fold forward over the steel rail. The rail tube runs in front of their torsos, which is correct, because the camera is inside the tank and the rail stands between the glass and the cast. Their heads stay behind the tube and well short of the glass. Nothing reads as a head stuck in the acrylic or a rail through a body. At 108.2 and 109.0 s, my face and Rosa's are calm, with closed eyes and small smiles.
- **S69 (132.4 to 134.68 s):** at 132.4 s the side framing holds on the pup over "followed my HAND." From 133.0 s it drifts back into the blue, and from 133.6 s it's whole in the frame, with its two rows of brown irises turned to the camera. The Regular fades to a faint shape at the left edge first. The pup's rows are the last thing lit. The eyes are wet and uncanny, with no red, no veins and no injury, the same as the rest of the film. The cast is out of frame.

There's nothing on screen in either shot I'd hold back. S69 stays off the cover list (package section).

## D. The whole-film flash measure

`safety.house_report` with the 68 cuts from `timeline.json` (written 10:06), on both sources. The higher count governs.

| Reading | Composed frames (4041) | Final mp4 (4041) | Bar | Round 2 final | |
|---|---|---|---|---|---|
| 1-frame flashes / changes, max per s | 1 / 3 | 1 / 3 | 2 / 5 | 1 / 3 | pass |
| 3-frame flashes / changes, max per s | 2 / 5 | 2 / 5 | 3 / 6 | 2 / 5 | pass |
| Red flashes, 1-frame and 3-frame | 0 / 0 | 0 / 0 | 1 | 0 / 0 | pass |
| Extended, 1f / 3f | 0 s / 0.70 s | 0 s / 0.70 s | under 4 s | 0 / 0.70 s | pass |
| Red frames | ok (max saturated-red share 0.224) | ok (0.225) | | ok | pass |
| Very different cuts, max per s | 1 (frames 641, 1517, 1551: 21.37, 50.57, 51.70 s) | 1 (the same 3) | 3 | 1 | pass |
| IRIS 25% reading (information only) | 1 / 2 | 1 / 2 | | 1 / 2 | |
| Transitions, 1f / 3f | 56 / 183 | 56 / 183 | | 56 / 185 | |
| **House bar** | **pass** | **pass** | | pass | |

- **The hot seconds** are the same three as round 2, all at 2 a second on the 3-frame reading, under the bar of 3:
  - 58.90 to 59.57 s (S34)
  - 66.53 to 67.17 s (S38, the film's peak of 5 changes)
  - 88.00 to 88.33 s (S47 into S48)
- **The tail:** S58 and S69 add nothing hot. The 3-frame count fell by 2 transitions (185 to 183). The only red change is still the one rise on the warm cut at 128.57 s (S67 into S68).
- **The seam** (`wrap_report`, frames 4011 to 4040 into 0 to 29): **0 transitions on every reading.** The last frame's luma is 0.039 and S01's first is 0.038, so round 2's fall at the loop is gone.
- **`bound.py`:** no cut flagged.

**The span (`span.py`, the same on both sources):**
- the first transition is frame 84, 2.80 s (S01 into S02)
- the last transition is frame 3967, 132.23 s (S69, the 3-frame reading)
- the last 1-frame transition is 130.83 s, the cut into S69

The package line, rounded out the same as rounds 1 and 2:

> Flashing lights and fast cuts from 0:02 to 2:13.

## E. L85 against the fiction, brand and word rules

**L85:** "It DRIFTED / into the BLUE, / still WATCHING me." Spoken: "It drifted into the blue, still watching me."
- ✓ **Fiction:** nothing is claimed as true. There's no "real", "true", "based on" or place name.
- ✓ **The ritual-back ending is gone:** no "back" and no returned gesture in L82 to L85. "Back" now appears only at L75 ("GLIDED BACK") and L78 ("came BACK"), and both are the Regular moving, not me returning a gesture. My bow key is gone too.
- ✓ **Brand and IP:** no game, toy or monster name. "Watching" and "eyes" are only words in the story here, not a monster's name.
- ✓ **Child and captive words:** no age, kid or baby word, and no "trapped", "captive", "held" or "zoo". "Pup" stays in L79 and L80 as an animal's young, the same as round 2.
- ✓ **Made for kids: No** still holds. The ending is the uncanny creature leaving while still watching, not a cute beat.
- ✓ **Voice:** `python -m studio voice` passes the line and the on-screen text of `03-reel.md` ("read as written by a person"). Its two warnings are the semicolon and the parenthetical list in the motion-designer's header paragraph, which nobody sees on screen.
- ✓ **Captions and voice:** `03-reel.md`'s last three captions are the three chunks above. The designer's `asr` heard L85 as written, with 0 words wrong. The fact-checker owns that check.
- **For the critic, not a standards item:** "into the BLUE" is now the third "the BLUE" in the last 30 s (L75, L78, L85). It reads as a callback, and nothing in it is a compliance risk.

## F. The channel, the batch and dark themes

Nothing changed since round 2, section F. The ending is now quieter: the creature leaves, the cast doesn't return a ritual, and nobody is harmed. That strengthens the "cohesive narrative, not repeated disturbing themes" reading. The spacing rule in days and the PandaNanoAdventures upload checklist carry over below.

## G. Fixes and owners

Nothing blocks approval.

| # | Item | Owner | Re-render? |
|---|---|---|---|
| carried | R3: replace the board title "Always wave goodbye to the big tank" with the package title. The merge note uses the package title | packager, producer | no |
| info | D1's "whole and 15% in" falls about 1 s short at the start of the glide (132.45 to about 133.5 s), as the designer recorded. That's the critic's and producer's call | critic, producer | only if they ask |
| optional | `03-reel.md` header: change "the round 2 patch" to "the round 3 patch" (or the reverse) so it's consistent. If this is edited, re-run `studio check --final` so QA doesn't go stale, as it did in round 2 | motion-designer | no |
| advisory | Spacing in days (round 2, section F): never on the day next to ep12, at least two clear days after ep12, and never next to ep11 | producer | no |

**Gate note:** if anything touches `03-reel.md`, `story.json` or the mp4 after 10:50:40Z, QA goes stale again. Re-run `python -m studio check ep13-closing-time --final` before `gate`. Any new encode changes the hash and comes back to standards.

## For the package (packager)

**The file**
- **Upload `history-sound/out/ep13-closing-time.mp4` with SHA-256 `c04ce50f139228b5e13e64d557e7aa015308f918e6a764475251549abaf0bd88`** (4041 frames, 134.70 s). This is the only cleared file. Round 2's `628529266a54…ebb965` has the S58 clip and must not ship.
- Re-hash right before upload. If the hash differs, don't upload: send the file back to standards.

**Upload settings** (set on this upload in PandaNanoAdventures' own Studio, never left to a channel default)
- **Channel: PandaNanoAdventures** (note 21) only. Not @BuhExplains, Packed, Buh or the philosophy channel.
- **Made for kids: No.**
- **AI use (altered or synthetic content): No.** It's an obvious cartoon with invented characters, a synthesized score and a TTS narrator, and no real person is shown or voiced.
- **Before upload, confirm each of these on the checklist:**
  - the channel's audience default is "No, not made for kids"
  - the old kids' videos are hidden
  - comment holds are on
  - ep11's About text is live
- Don't add a song at upload. No YouTube hashtags until the first `/retro`.
- **Spacing:** never on the day next to ep12, at least two clear days after ep12, and never next to ep11.

**The description**
- **It opens with:** `Flashing lights and fast cuts from 0:02 to 2:13.` (confirmed on this file)
- Never write "no flashing", "flash-free", "epilepsy safe" or "photosensitive friendly".

**The title**
- **Not imperative.** The board title "Always wave goodbye to the big tank" doesn't ship, and neither does any "Do X" or "Never X".
- Not ep12's "When X, do Y" shape, not ep11's "The X counted 6. I counted 5." shape, and no "it wasn't X, it was Y".
- Avoid a bare "Closing Time" (04-decision-r2). The audience pick, "Why the night shift waves at the big tank", is fine: it's a question, not an order.
- It stays in-world, reads as a story, and leads with the eyes or the stare, never the pup.
- **New with L85:** don't build the title on "back", "waved back" or "returned the wave". The film no longer ends that way.

**Words to avoid** (title, description, pinned comment, tags and channel replies)
- "Roblox" or any game or toy brand, including in replies to "what game is this". Also "DOORS", "Seek", "Eyes" as a monster name, or any game monster.
- "true story", "real", "based on", "this happened".
- "teen", "kid", "kids", "baby", "pup", "cute", "aww", "family", "school trip", "field trip", or any age ("19", "nineteen").
- "human zoo", "trapped", "prisoners", "captive", "held".
- "AI voice", "no AI", "made by hand", "100% original". Don't name Kokoro.
- No real aquarium, city or place. No fish, whale, dolphin or heart emoji.
- Nothing that describes Dev or Rosa by race or skin.

**The cover and thumbnail**
- Use a real-eyes frame: the L55 POV stare (about 78.6 to 79.7 s, S43) or the S42 brown eye (about 76.7 s, "like a PERSON'S.").
- **Never:**
  - a pup frame (anything from L79 "a tiny PUP" to the end, including all of S69, 130.83 to 134.70 s, and the last frame)
  - Rosa's S06 or S10 close-up (S10 is the frame closest to a stock avatar look)
  - S58, the bow

**Copy:** every viewer-facing line goes through `python -m studio voice`. Standards and the fact-checker sign the package.
