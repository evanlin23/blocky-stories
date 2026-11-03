# The engine (`blocky/`)

How a story is built and rendered. The house rules are in `RULES.md`; this is the reference for `story.json`, `set.py` and the commands.

## Files

| File | What it does |
|---|---|
| `kit.py` | Blender parts: boxes, cylinders, plastic, glass, brick, cobbles, planks, concrete, metal, emissive, lights with flicker, game-engine distance fog, render setup, camera; CC0 photo textures (`texture`) and HDRI lighting (`world_hdri`) from `assets/` |
| `rig.py` | the R6-style character: box torso 2 x 2 x 1, arms and legs 1 x 2 x 1, a soft rounded-cylinder head with a drawn face, block hair, hats, patterned clothes (plaid, knit, stripes) |
| `faces.py` | our own drawn faces (PIL): eye styles and expressions, mouths that open, blinks, tears. It refuses the game's default-face look |
| `acting.py` | where every character is and what it's doing at time t: walking with leg swing, facing, arms, head, expression |
| `timeline.py` | places the lines, captions (two or three words), mouth flaps and shots from the word timings |
| `voice.py` | Kokoro (Apache 2.0) reads each line, then it's sped up (tempo and pitch up together); Whisper word check |
| `bl_story.py` | the Blender driver: builds the story's set and cast, poses them, moves the camera, renders frames |
| `post.py` | scale up, bloom, the story's grade, effects (flash, blackout, static, red, shake, punch-in, rain), grain, captions; H.264 |
| `sound.py` | the generated score, ambience, footsteps from the acting, one-off effects, the narrator, the master; recorded CC0 steps, ambience and a few effects from `assets/audio/` |
| `checks.py` | the checks behind `check` and the tests |

## story.json

```jsonc
{
  "slug": "ep11-...",            // the production (epNN-name, the upload order)
  "title": "working title",       // never the game's name
  "made_for_kids": false,         // required, always false
  "premise": "...", "twist": "...", "world": "...",   // compared against every other story by `check`
  "voice": {"voice": "am_adam", "tempo": 1.03, "rate": 1.45},  // the owner's pick at the look test
  "key_color": "#ffd640",        // the caption key-word colour for this story
  "gap": 0.12,                    // seconds between lines
  "look": {"fog": "#1c2230", "fog_density": 0.05, "fog_start": 3.0, "sky": "#0d1018", "exposure": 0.0,
           "hdri": "moonless_golf", "hdri_strength": 0.5, "hdri_rotation": 0, "hdri_visible": false},  // hdri: optional
  "grade": {"shadows": [-0.03, 0, 0.06], "highlights": [0.04, 0.01, -0.04], "saturation": 1.0,
            "contrast": 1.05, "vignette": 0.35, "bloom": 0.35, "grain": 0.012},
  "rain_shots": ["S1"],           // optional
  "tail": 0.9,                    // seconds after the last word; 0 ends on picture (a loop), no fade at either end
  "fade_out": true,               // optional; false keeps the picture bright to the last frame (no dip to dark in the last 0.2 s) when a tail is set
  "cast": {"me": {"age": "adult", "skin": "#f1c9a0", ... rig.py's spec ...}},
  "lines": [
    {"id": "L01", "who": "narrator", "chunks": [["In this TOWN,", "In this town,"], ["nobody SLEEPS.", "nobody sleeps."]]},
    {"id": "L07", "who": "mom", "chunks": [["Close it,", "Close it,"], ["NOW.", "now."]]},
    {"id": "P1", "pause": 0.8, "chunks": [["THUD", ""]]},   // a beat with no words, an optional big word
    {"id": "P2", "pause": 1.6, "chunks": [["KNOCK", ""], ["KNOCK", ""]], "times": [0, 0.5]}  // its words pop in turn
  ],
  "shots": [                      // the first starts at 0; each other starts at its "at"
    {"id": "S1", "cam": [[0, [x, y, z], [tx, ty, tz], 28], [1, [...], [...], 32]], "step": 2},
    {"id": "S2", "at": "L03.1", "follow": "me", "cam": [[0, [0.3, -1.3, 1.5], [0, 0, 1.5], 45]], "hand": 0.02, "step": 1}
  ],
  "acting": {"me": [{"at": 0, "pos": [0, 4], "yaw": 0, "expr": "worried"}, {"at": "L02", "pos": [0, 4]},
                    {"at": "L03", "pos": [0, 1], "expr": "scared", "run": true}]},
  "cues": [{"at": "L05.2", "name": "lights_out"}],    // read by set.py's animate()
  "fx": [{"at": "L06", "kind": "shake|flash|black|static|red|punch", "dur": 0.4, "amp": 1, "fade": 0.2, "zoom": 1.15}],
  "music": {"root": 50, "mode": "minor|phrygian|dorian|harmonic|locrian|major|whole", "bpm": 72, "seed": 3,
            "sections": [{"at": 0, "voices": ["drone", "pad", "musicbox", "piano", "pulse", "choir"], "energy": 0.4}]},
  "sound": {"floor": "stone|concrete|wood|metal|grass|gravel|snow", "steps_db": -20,
            "rev": 2,                   // optional, ignored by the mix: bump it to have a story with a film drawn again
            "samples": true,            // optional; false: every step, ambience and effect synthesized, as before 2026-11-03
            "ambience": [{"kind": "wind|hum|rain|room|drips|crickets|traffic|water|drone|static", "from": 0, "to": "end", "lufs": -32}],
            "sfx": [{"at": "L06", "kind": "hit|riser|whoosh|creak|door|knock|glitch|bell|thud|sting|click", "db": -8, "dur": 1.0},
                    {"at": "L08", "kind": "door", "synth": true},   // synth: keep the synthesized door, not the recording
                    {"at": "P2", "kind": "knock", "pattern": [0, 0.2], "tone": "below|hand|glass|soft|glass_soft"}],
            "music_drops": [["L09", "L10"], {"from": "L12", "to": "L13", "keep": ["sting"]}]},
  "phonemes": {"Name": "nˈAm"}    // misaki phonemes for made-up names
}
```

**Time references** (anywhere an `at` goes): seconds, `"L03"` (the line's first word), `"L03.2"` (chunk 2's first word, 0-based), `"L03>"` (the line's last word ends), `"L03.2>"`, offsets like `"L03+0.4"`, and `"end-1.5"`. A pause beat's id works the same way (`"P02"`, `"P02>"`, `"P02-0.3"`).

**Pause beats** show their big words one chunk at a time: at the beat's `times` (seconds into it), or spread evenly. A
three-knock beat puts one KNOCK on each knock, where three big words wouldn't fit in two lines.

**Knocks** (`sfx` kind `knock`): a `pattern` of hit times in seconds (default three even thumps), optional `gains` per
hit, and a `tone`: `below` (deep and muffled, up through boards), `hand` (a knuckle on planks), `glass` (a door with a
pane that rattles after), `soft` (bone on wood, close and quiet) or `glass_soft`.

**A score section** can set its own `mode` and `root` (a turn to the relative major for a few bars, then back).

**One voice** (owner, 2026-10-30): voice A (`am_adam`, tempo 1.03 x rate 1.45) reads every line, and what
characters say is reported by the narrator ("He said, "Six.""). `voice.py` can still read a cast member's lines
with their own `cast.<name>.voice` (it merges over `voice`, and picks Kokoro's British pipeline for `bf_`/`bm_`
voices), but that support is **unused**: no story gives anyone a voice of their own.

**Music drops** are real holes: from `from` to `to` (anchor both to line ids, so a retime can't move them off
their words) the music, ambience, footsteps and sound effects fall 40 dB, and only the voice plays on, plus any
`sfx` entry marked `"keep": true` or of a kind the drop lists in `keep` (the sting that lands in the hole).

**Acting keys**: `pos` [x, y] or [x, y, z] in metres is where the character is at that moment, so between two keys it walks there and its legs swing with the distance. Two keys at the same pos make it stand. While walking it faces where it's going. `yaw` (degrees, 0 faces -y), `arms` [left, right] raised forward, `side` [left, right] out, `head` [yaw, pitch] and `lean` hold, then ease to the next key over `blend` (0.25 s). `expr` (neutral, worried, scared, crying, angry, smirk, blank, wide, shut, grin, terrified, squeeze), `look` [x, y], `hidden`
and `blink` (false holds the eyes open) switch at their key; `tremble` (degrees) is a small fast head shake. A mouth key
`{"from": ref, "to": ref, "mouth": [a, b]}` opens a mouth from a to b (0..1) whether the character speaks or not, and
takes the larger of it and the talking flaps; a "line" seam still only parts into a slit. With `"flap": true` it flaps
open and shut about every 0.11 s, for a character whose words the narrator reports (one voice). A character 1.75 m tall has its eyes at about 1.55 m.

**set.py** defines `build(kit, story, tl)`, which makes the world from `kit`'s parts and returns a dict it can keep. An optional `animate(kit, story, tl, t, ctx)` moves story things each frame (a door, a light going out, something rising) and may return `{light name: gain}`. `timeline.cue(tl, name)` gives a cue's time.

## The CC0 library (`assets/`)

Owner, 2026-11-02: "yes go ahead with sfx and visuals". Every file is CC0 and listed, one row each, with its source,
author and date in `assets/LICENSES.md` (a test fails on any file without a row). About 29.5 MB in all. The score stays
synthesized; characters, faces and their materials stay ours (RULES.md hard rules 4 and 6).

**Sound** (`sound.py`, automatic whenever the files exist; the synth is the fallback):
- **Footsteps** (`assets/audio/steps/<surface>/`): grass (8), wood (7), stone (9, also used for `concrete`), metal
  (10), gravel (6), snow (8). Each step picks a seeded file, changes its speed by up to 3% and its level by up to
  1.5 dB, and is matched to the loudest 50 ms of the synthesized step it replaces, so `steps_db` still means what it
  did. Running steps are 2 dB up.
- **Ambience loops** (`assets/audio/amb/`): `wind`, `rain`, `room` (a low fridge-and-room drone), `crickets` (far
  off), `traffic` (distant, low-passed; new, with a synthesized rumble as its fallback) and `water` (a river). Seamless
  loops, started at a seeded point and tiled to length; the ambience `lufs` sets the level as before. The other kinds
  (hum, drips, drone, static, beehum, gulls, fire) are still synthesized.
- **Effects** (`assets/audio/sfx/<kind>/`): `door` (4 closes), `creak` (3, cut to the entry's `dur`), `latch` (3),
  `whoosh` (4) and `thud` (3), each at the synthesized sound's level. `"synth": true` on an entry keeps the old sound,
  and so does a creak with a `tone` (cardboard). Every other kind is synthesized.
- Steps and ambience keep under 5% of their energy above 4 kHz (the files were low-passed until they did, and a test
  checks every file and every sampled step and loop). `"samples": false` in `sound` turns the library off for a story,
  and the environment variable `BLOCKY_NO_SAMPLES=1` turns it off for a run.
- `sound.rev` does nothing in the mix. A story's film is drawn again when a file in its folder changes, and an engine
  change isn't one, so bump `rev` in a story that should pick up new sounds.

**Lighting** (`look.hdri`, opt-in): a Poly Haven HDRI from `assets/hdri/` lights the scene, soft sky light and
reflections, at `hdri_strength` (default 0.5) turned `hdri_rotation` degrees. The camera still sees `sky` (the fog
colour), so the look, the fog and the frame are unchanged and no real place shows; `"hdri_visible": true` shows the
HDRI itself. Keep the set's own lights: the HDRI fills, it doesn't key. Names: `moonless_golf` and
`satara_night_no_lamps` (night), `kloppenheim_06_puresky`, `evening_road_01_puresky` and `industrial_sunset_puresky`
(dusk), `overcast_soil_puresky` (flat grey day), `lebombo` (a daylit room). `check` blocks a name that isn't there.

**Textures** (`kit.texture(name, scale=1.0, tint=None, rough=None, bump=0.25)` in `set.py`): `brick`, `wood`
(weathered planks), `concrete`, `grass` and `asphalt`, 1k colour and roughness maps, box-projected in object space (our
blocks have no UVs), one tile per metre at scale 1 (scale 0.5 makes them twice as big), with a small bump from the
colour and the distance fog like every other material. `tint` (a hex colour) multiplies the colour, to keep a set's
palette or the "closer" style's brighter look. Missing files fall back to the procedural brick, planks, concrete or
a grime colour. `check` blocks a texture name that isn't one of these.

```python
def build(kit, story, tl):
    kit.box("road", (20, 6, 0.1), (0, 0, -0.05), kit.texture("asphalt", 0.5))
    kit.box("wall", (6, 0.3, 3), (0, 3, 1.5), kit.texture("brick", 1.0, tint="#d8c8c0"))
```

**Props:** none yet. Quaternius (CC0) serves its packs only through a Google Drive folder that needs a browser, so
nothing was taken from it.
