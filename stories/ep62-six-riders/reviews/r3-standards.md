# ep62-six-riders, round 3, standards (rescue look)

r2 must-fix:
- **Flash at P02 / S19: fixed.** P02 is now 1.1 s, and S19 holds the "1" from 23.57 to 24.67 s. That puts the S18 to S19 and S19 to S20 cuts 1.1 s apart, so they're no longer inside one 1 s window. I ran `python -m blocky flash ep62-six-riders --file out/work/ep62-six-riders/ep62-six-riders-preview.mp4` myself:
  - 3-frame reading: **2 flashes and 4 changes**, worst at 27.13 s. The target was at most 2 and 5.
  - General reading: 1 flash and 2 changes.
  - Red reading: 0.
  - Bright cuts: 0 very different.
  - House bar: PASS.
  - The extended run is 0.27 s from 22.4 s.

  This is the preview reading. The final is measured on Actions.

Regression look (contact sheet, `check`, the diff since r2):
- The new beats are S05b (punch in on C and D), the split letter lines L04a to L04d, the S13 reframe, all four riders out of S15, and the glass tint at 0.10. None of them adds a sign, real name, young-looking figure or copied item.
- Everyone on screen is still an adult at full height.
- `script.md` and `package.json` haven't changed since r2. Their r2 passes for fiction, IP and package still hold.
- `check`: no blocks. Its one warning is 211 wpm, which is pacing and not a standards issue.

No must-fixes.

Verdict: approve
