Verdict: approve

# moving-day r7: standards

1. Fiction: pass. S01's new frame has no text. Nothing else changed.
2. Kids and mature themes: pass. Everyone is an adult, and nobody young-looking is in peril.
3. IP: pass. No game name anywhere, and nothing copied.
4. Originality: pass. Same as r6.
5. Flashing: pass. The house bar holds with confidence.
   - The 3-frame peak at 3.5 s comes from the preview, not the edit. `frames-preview` still holds stale frames from the 01:17 render (f00129, and f00133 to f00169 every 4th, on the old S04 grid), mixed in with the 02:03 re-render. Frame 129 shows one frame of the pink S04 house inside S03, then S03 comes back. I swapped those 11 frames for their neighbours and measured again. The opening then reads 1 flash and 2 changes (1-frame) and at most 1 to 2 flashes (3-frame). The r6 retime works. The final is drawn fresh on Actions, so the stale frames can't reach it.
   - What's left is 3 flashes and 6 changes at 10.97 to 11.03 s. That's the S07 to S08 and S08 to S09 cuts, both mixed and 0.83 s apart. It sits exactly at the cap and passes. The count is fixed by the cut structure: each mixed cut scores 3 alternating changes, and no 1-frame transition falls between them. The final moves more smoothly than the preview, so an extra change inside S08 is unlikely. The 25% reading is 1, the extended reading is 0.53 s, red is 0 and bright cuts are 2. S01's grey ceiling isn't clipped.
6. Package: pass. The title, description ("It's made up."), pin and `cover_s` are unchanged and clean. `hold` stays, as asked.

## Must-fix

None.

## Nice-to-have

- Builder: empty `out/work/moving-day/frames-preview` before re-rendering only part of a preview. Stale frames at other steps get encoded in and distort the flash reading.
- S08 (11.03 to 11.87 s): at 1.0 s or longer, its two mixed cuts would sit in separate seconds and the film would get margin under the cap.
