# ep127-thousand-tellings: standards, rescue look (round 3)

Verdict: approve

I checked against the fresh full-rate flash film (`picture-flash.mp4`, drawn 09:13 to 10:13) and the re-rendered preview, both after the rescue commit 4f58e5e8. I scanned the luma of every frame.

## Fix check
1. **S45 (L24, 40.1 to 41.33 s): fixed.** The pool of light on the gravel is lit from frame 1203, the shot's first frame. Luma holds at 87 to 90 across the shot, with a largest step of 0.6. The preview reads 87 to 89. Nothing snaps on.
2. **S21 (L10, car leaving, 19.1 to 20.33 s): fixed.** No trunk crosses the lens and no frame is near-black. Luma falls smoothly from 191 to 150, and the largest one-frame step is -8 as the camera tilts onto the road. The frames show the car the whole way.

## Regressions
- **Car fill, L44 and L45 (S79 to S83, 67.87 to 71.1 s):** the warm dash light is steady. The steps inside each shot are 1.8 or less, apart from S81 at 3.4, and the faces read clearly.
- **Night fill gating:** I scanned every shot for any in-shot step of 5 or more, or a range over 25. Only S13, S21, S31 and S85 showed up. S13 is cubes flying past in daylight, S21 is fix 2 above, and S85 is him walking into the doorway. S31 is covered below. None of them is a light switching. Every one-frame jump over 40 falls on a cut, and no frame is darker than luma 51.
- Preflight: flash PASS (3282 frames), with a 3f peak of 3/s at 24.87 s. 0 blocks.

## Should-fix (not blocking)
- S31 (L15 "The first night, I came back late", 26.47 to 27.63 s): his face starts in shadow and brightens as he walks into the fill. Luma climbs smoothly from 60 to 143 over 1.2 s, which isn't a flash. If you want, place the fill at a fixed `fill_at` so his face is lit from the first frame.
- Carried over: S114, hold 999 until "one THOUSAND". `check` still warns on L28 (the slogan pattern) and on the "of it," caption, which runs under 0.2 s.
- package.json `hold` must come out before merge.
