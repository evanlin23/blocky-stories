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
| `polish.py` | the polish pack (`look.polish`): cut whooshes, key-word and reveal hits, risers, the room bed, punch-ins, drift, sway, the bright grade, the caption pop |
| `checks.py` | the checks behind `check`, `preflight` and the tests: the rules, the pace and the stills the edit already holds, and the clip report |

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
  // look.polish: true turns on the polish pack (see below); a dict overrides its settings
  "tail": 0.9,                    // seconds after the last word; 0 ends on picture (a loop), no fade at either end
  "fade_in": true,                // optional; false skips the 4-frame fade up from black at the start (a loop that cuts straight into frame 0)
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
  "sound": {"floor": "stone|concrete|wood|metal|grass|gravel|snow|carpet", "steps_db": -20,
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

**Splitting captions in a generator** (2026-11-05): `timeline.split_lines(lines)` splits every [caption, spoken]
chunk into two- or three-word captions and returns `(lines, chunk map)` for remapping `"L07.2"` references. Use it
instead of a copy of the old splitter, which sliced the spoken words by the caption's word count and dropped any
left over ("has said 4:12" voiced "has said four", ep115 L19). Where the counts match it gives exactly what the
old copy gave. `check` warns and `preflight` blocks when a line's spoken words in story.json differ from the
story's `generator/lines.json`.

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

## Before any render: the stills and the clips (2026-11-03)

The preview is quarter-res with every 4th drawing, so a face through a boot, a picture that holds still too long
and the pace were invisible until the final. Two checks read them before a frame is drawn:

- **Stills** (`checks.still_spans`, pure python): a stretch inside one shot where the camera (its keys, `follow`
  and the polish pack's move), the crop (punch-ins, drift, sway) and every character's pose all hold. Over 1.0 s is
  what `measure.py` blocks a film on (`macro.longest_still_q_s`), so `preflight` blocks on it and `check` warns.
  Key a move, a pose or a punch-in there. A shot where `set.py`'s `animate` moves something big instead is exempt:
  list it in story.json `"set_moves": ["S14"]`.
- **Clipping** (`python -m blocky clipcheck <story>`, Blender, no drawing: about 2.5 minutes for a 2-minute film).
  The scene is posed every 0.25 s and at every acting key, and each head on screen is tested against every other
  rendered mesh with a BVH overlap, the head shrunk 10% so a touch isn't a hit. The heads are the cast's, plus any
  set object whose name starts with one of story.json `"clip_heads": ["chead"]` (a creature `set.py` builds itself).
  An overlap the story means to have (a cat through its own flap, a face against the glass) goes in
  `"clip_ok": ["flap", "S58/pane", "S97"]`: an object name, a shot, or a shot and an object. Anything else blocks.
  `preflight` runs it when `BLOCKY_BPY` is set, and the proof workflow runs it on the PR.

## The local flash check (`python -m blocky flash <story> --like-proof`, 2026-11-05)

The preview's flash reading is indicative only. It draws every 4th frame and holds each drawing for 4, so a light
that flips brightness every 1 to 3 frames (a glow, a ring stamp, a lit closet) reads at half its rate there, or
not at all when the flip lands on the same phase every time. ep97, ep101 and ep107 passed the preview at about 4
a second and failed the proof at 7 (or on a 4.9 s extended run). `flash --like-proof` draws the proof's own frame
list (every drawing) at the meter's analysis size (135 x 240, `safety.LOW`, 4 samples) into `frames-flash/`,
finishes `picture-flash.mp4` and measures it. On ep107 S49 to S56 it read the proof's numbers second for second,
for about 1.4 times the preview's drawing time. `--shots S12,S13` redraws only those shots after a fix and keeps the
rest. `preflight` reads that picture when there is one, and blocks on it.

## The proof render (`.github/workflows/proof.yml`)

The whole film, before merge, the way the final will be: every drawing the final makes (no frame skipping), at
270 x 480 with 4 samples, through the same engine path as `render.yml` (`python -m blocky render --proof`, then
`finish --proof` and `mix --proof`, which still finish at 1080 x 1920), with the narration made on Actions. It
runs on a story PR once both reviews approve, or by hand with a story and a ref. It keeps `proof-<story>` for 14
days (the film, the contact sheet, `flash.json`, `craft.json`, `clip.json`, `mix.json`, `proof.json` with the
commit it drew, and `verdict.json`), posts the craft table in the job summary, and fails on a craft block, the
flash bar, a clip or a true peak over -1 dBTP. The qa agent checks that artifact and writes `qa/<story>.json`
with `"stage": "proof"`; `test` blocks the merge without it (`python -m blocky gate <story> --merge --base <sha>`).

## The CC0 library (`assets/`)

Owner, 2026-11-02: "yes go ahead with sfx and visuals". Every file is CC0 (each pack's own licence file is in
`assets/licenses/`) and listed, one row each, with its source,
author and date in `assets/LICENSES.md` (a test fails on any file without a row). About 35 MB in all. The score stays
synthesized; characters, faces and their materials stay ours (RULES.md hard rules 4 and 6).

**Sound** (`sound.py`, automatic whenever the files exist; the synth is the fallback):
- **Footsteps** (`assets/audio/steps/<surface>/`): grass (13), wood (12), stone (14, also used for `concrete`), metal
  (10), gravel (11), snow (13) and carpet (5, new: a muffled synthesized step is its fallback). Each step picks a seeded
  file, changes its speed by up to 3% and its level by up to 1.5 dB, and is matched to the loudest 50 ms of the
  synthesized step it replaces, so `steps_db` still means what it
did. Running steps are 2 dB up.
- **Ambience loops** (`assets/audio/amb/`): `wind`, `rain`, `room` (a low fridge-and-room drone), `crickets` (far
  off), `traffic` (distant, low-passed; new, with a synthesized rumble as its fallback) and `water` (a river). Seamless
  loops, started at a seeded point and tiled to length; the ambience `lufs` sets the level as before. The other kinds
  (hum, drips, drone, static, beehum, gulls, fire) are still synthesized.
- **Effects** (`assets/audio/sfx/<kind>/`): `door` (8 closes), `creak` (6, cut to the entry's `dur`), `latch` (5),
  `whoosh` (4) and `thud` (10), each at the synthesized sound's level. `"synth": true` on an entry keeps the old sound,
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

**Props** (`kit.prop(name, loc=(0, 0, 0), rot=0, scale=1.0, height=None, fit=None, tint=None, parent=None)` in
`set.py`, opt-in): 86 CC0 models in `assets/props/`, from the owner's download of Quaternius and Kenney packs
(2026-11-03, PR #102). Each is one self-contained .glb in metres beside our 1.75 m characters, origin at the bottom
centre, so `loc` is where it stands; `rot` turns it about the vertical in degrees. `height` (m) or `fit` (its largest
side, m) sizes it, otherwise `scale`. `tint` multiplies every colour, to fit the set's palette or the "closer" style.
Its materials go through the distance fog like ours, and repeats share one mesh. `kit.props()` gives the list with
each prop's size (`assets/props/props.json`), and `check` blocks a name that isn't there. No characters, creatures,
weapons, lettering or signs: the cast is always built in `rig.py`. Props dress a set; the set's own look (blocks,
plastic, fog) still leads, so a few well-placed pieces beat a catalogue.

- Quaternius Ultimate House Interior (furniture, kitchen, bathroom, doors, windows, lamps): `bathroom_bathtub`, `bathroom_sink`, `bathroom_toilet`, `bed_king`, `bed_single`, `bookshelf`, `carpet_1`, `chair_1`, `chair_2`, `couch_l`, `couch_medium1`, `curtains_double`, `door_1`, `door_double`, `drawer_1`, `fireplace`, `houseplant_1`, `kitchen_cabinet1`, `kitchen_fridge`, `kitchen_oven`, `kitchen_sink`, `light_ceiling1`, `light_desk`, `light_floor1`, `nightstand_1`, `shelf_1`, `stool`, `table_roundlarge`, `table_roundsmall`, `trashcan_cylindric`, `window_large1`, `window_small1`
- Quaternius Ultimate Nature (trees, bushes, rocks, stumps, logs, grass): `birchtree_1`, `birchtree_dead_1`, `bush_1`, `bush_2`, `bush_snow_1`, `commontree_1`, `commontree_2`, `commontree_dead_1`, `commontree_snow_1`, `flowers`, `grass`, `grass_short`, `pinetree_1`, `pinetree_2`, `pinetree_snow_1`, `plant_1`, `rock_1`, `rock_3`, `rock_5`, `rock_moss_1`, `rock_snow_1`, `treestump`, `willow_1`, `woodlog`, `woodlog_moss`
- Quaternius Ultimate Buildings (1 to 4 storey town houses; the signed ones left out): `bldg_1story`, `bldg_1story_gableroof`, `bldg_2story`, `bldg_2story_balcony`, `bldg_2story_slim`, `bldg_3story_small`, `bldg_4story`
- Kenney Nature Kit (fences, gate, log stack, stump, campfire stones, bridge, tent, pot): `nat_bridge_wood`, `nat_campfire_stones`, `nat_fence_gate`, `nat_fence_planks`, `nat_fence_simple`, `nat_log_stack`, `nat_pot_large`, `nat_stump_old`, `nat_tent_detailedclosed`
- Kenney City Kit Suburban (houses, fences, driveway, paths, planter, trees): `sub_building_type_a`, `sub_building_type_c`, `sub_building_type_f`, `sub_building_type_k`, `sub_building_type_p`, `sub_driveway_long`, `sub_fence`, `sub_fence_1x3`, `sub_fence_low`, `sub_path_stones_long`, `sub_planter`, `sub_tree_large`, `sub_tree_small`

```python
    kit.prop("pinetree_1", (-4, 9, 0), rot=30)
    kit.prop("sub_fence", (0, 3, 0), height=1.1, tint="#d0c8c0")
    kit.prop("bed_single", (1.2, 2.0, 0), rot=90)
```

## The polish pack (`look.polish`, `blocky/polish.py`)

Opt-in per story, and on for every new story since 2026-11-03 (owner, 2026-11-03: "make them high quality or keep
pushing the quality up"). Only proven moves; the before/after on ep32-sitter is in `docs/research/polish-pack.md`.
`"look": {"polish": true}` turns it all on; a dict changes any setting:

```jsonc
"look": {"polish": {"emph": ["L03.1", "L19"],   // lines to punch in on (default: the hook and every all-caps caption or big word)
                    "reveal": ["L38"],          // a fuller hit (big pause words are always reveals)
                    "twist": "L34",             // a riser that ends here (risers also run into every music_drops hole)
                    "quiet": ["L36.5", ["L35", "L37"]],   // no hit on a word; no whoosh, hit or added punch-in in a span (a warm beat)
                    "auto": true,               // also punch in on all-caps captions, big words and the hook (default)
                    "sway": ["S12", "S13"],      // gentle handheld on tense shots (true: every shot)
                    "bed_kind": "rain",          // the bed (default: the story's most-used recorded ambience, else room)
                    "punch": 0.06, "punch_rate": 0.7, "camera": true, "ease": true, "idle": true, "ones": "walk",
                    "drift": 0.03, "whoosh_db": -19, "grade": "bright"}}
```

- **Sound** (v2.2, owner 2026-11-03: the hits use few effects, and there is background music): the score plays under
  the whole film (`polish.music_spec`: the first section starts at 0, and a section with no drone, pad or choir gets
  a quiet drone and pad; holes only at `music_drops`). A recorded whoosh, low-passed at 3 kHz, 0.12 s before every
  punch-in (on cuts between lines too only with `"whoosh_cuts": true`); one low hit on the hook (`"key_hits":
  "all"` for every key word, 4 s apart); a soft sub thump on emphasised words and a fuller hit on
  reveals, each moved onto the chunk's key word (`on_key`); a 1.8 s riser into the `twist` and the `music_drops` holes (the silence
  cuts it off; the voice doesn't duck it), at most one per 15 s (`riser_gap`); a room bed from `assets/audio/amb/` under the whole film at -44 LUFS (12 dB lower again wherever the story has its own ambience),
  which a drop only dips 12 dB, so nothing is ever digital silence. Doors and other marks: an acting key with
  `"sfx": "door"` (or `latch`, `creak`, `thud`, `knock`; `sfx_db` sets its level) plays it there, panned to the
  character; so does a cue named `door...`. Every polish sound stays clear of the builder's own `sfx` (0.25 s),
  keeps under 5% of its energy above 4 kHz (tested), and the bed, the polish sounds and the ambience duck 8 dB under
  the voice. The music then dips under the lines by the least of 0, 2, 4 or 6 dB that puts the voice
  `voice_gap_db` (10.5 dB) over the music and ambience together (`music_duck_db`: "auto", or a fixed dB). The master is unchanged (-14 LUFS, true peak under -1 dBTP on the file).
- **Captions:** pop in from 90% to 100% over 80 ms (the default is a slower overshoot).
- **Motion**, on the output crop, so it's smooth on every frame even with drawings on twos or fours: a 6% punch-in
  eased over 0.12 s on key words, held to the cut (capped, see Punch-ins; `fill` can add one in any long shot); a 3% drift (in or out, with a slight slide) on every shot
  over 1.5 s whose camera doesn't move; an optional slow sway. All of it reads as no change to `flash`.
- **Acting** (v2, craft metrics 2026-11-03), through `tl["motion"]`, which only the pack sets: `ease` gives every walk
  that doesn't carry on into another a trapezoid of speed (0.25 s to get going and to stop, longer for a run:
  speed / 4 m/s²), same keys and timing, with the footsteps on the eased distance; `idle` gives anyone standing slow
  breathing (6 mm), a weight shift (about 1°), a turn of the body (2°) and a drifting head (5° and 2.5°), from sines
  at periods that never line up, added on top of their keys. `ones: "moving"` (the default since 2026-11-03, the lead's call)
  draws every shot whose camera moves, or where someone walks, on every frame, so the pack's camera moves don't
  judder at 15 drawings a second. With the pack that's nearly every shot: 1.87 to 1.98 times the drawing, about
  30 min more on Actions for a 140 s story. `ones: "walk"` is the opt-out for a long story whose render would run
  over about 2 h: only walking shots on every frame (about +9%).
- **Camera** (v2): `camera` gives every shot whose own camera holds still (one key, no `follow`) a slow push-in of
  `cam_push` (7%, at most 0.6 m) with a `cam_arc` (3°) arc round the target, the arc turning the other way shot to
  shot, and every third shot a slow truck. `polish.cam_spec` is read by both `bl_story.py` and
  `scripts/measure.py` (through `polish.cam_specs`). The whole move is at most 0.12 m/s, a camera under 2 m from its
  target pushes proportionally less, and a shot a reveal lands in gets a straight push at half speed with its
  characters' idle motion at a fifth (`tl["motion"]["calm_shots"]`). The 2D drift then only covers shots it doesn't.
- **Pace** (v2.3, the craft-metric blocks from 2026-11-03): a steady crop push through every shot (`push`, 12%
  across it, in on one shot and out on the next, at a constant rate), and inside any shot over 1.6 s an angle cut
  about every second (`reframe_every`): every other part is a 1.14× tighter framing, centred, like a second camera. Reveal shots and shots touching a quiet span get no angle cut and half the push. The push scales
  with shot length (full at 2 s, so a short shot doesn't rush), angle cuts are centred and land on a caption change,
  and `"hold": ["S29"]` keeps a frame-exact shot (a comparison, a doorway) at crop 1.0. The pack's crop never
  goes past 1.18× (`max_zoom`: the drawings are 540 wide, and past that it goes soft). The bright grade keeps every pixel under WCAG's saturated
  red (`red_line` 0.78), because the tighter crops enlarge red areas.
- **Punch-ins** (v2): key words only (the builder's `emph`, the hook, big words, all-caps captions, a key word that
  ends its line), at most `punch_rate` (0.7) per 10 s, evenly spread. Hits keep their own 4 s spacing.
- **Picture:** the `bright` grade raises exposure to at least 1.12 (v2.3) and saturation to 1.1, caps contrast at 1.05,
  the vignette at 0.2 and grain at 0.009, and adds a toe that lifts the darkest tones instead of crushing them (by scaling each pixel with its
  luma's lift, so colours keep their saturation). The
  story's own tints and shot grades stay.
- `check` blocks an unknown setting, a `sway` shot that doesn't exist, a punch over 8% and a bed with no recording.
