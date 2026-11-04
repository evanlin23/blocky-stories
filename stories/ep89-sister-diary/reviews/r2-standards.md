# ep89-sister-diary: standards, round 2

Verdict: revise

Checked: the script, package.json and story.json, the preview contact sheet (122.4 s), the fix-1 stills sheet, preflight (0 blocks, flash PASS), frames pulled with ffmpeg at every old black shot and at the cover, and a luma scan of every frame in the preview.

Round 1 fixes hold:
- **Opening:** L01 has the `must` shape and `"opening": "must"` matches it. Batch 8 now has 1 `confess` in 5, and the queue has no two of one opening in a row.
- **Old black shots:** S17 (21.0 s), S26 (32.5 s), S28 (34.7 s), S65 (75.0 s) and S78 (94.1 s) are lit now, and the inset is clear in each.
- **Cover:** 71.0 s lands in S62. It shows Nina full face, `terrified`, under "TERRIFIED.", and the frame is clean.
- **Other changes:** L12, L70 and the new description are fine. Fiction, kids, IP and originality still pass. `hold` is left in on purpose, as noted.

## Must-fix
1. **Two shots are still black (picture, light drop).** The luma scan finds two stretches where the frame is full black and only the inset and captions show. Both cut straight in from a lit frame and straight back out:
   - **S35, 40.43 to 40.67 s (L24, "I shut it."):** the camera at [-0.805, 2.15, 1.2] sits behind the diary lid as it closes. Pull it back and up so the lid never covers the lens. S17's fixed start, [-0.95, 2.25, 1.35], works.
   - **S59, 65.77 to 67.07 s (L41, "Her door ... an INCH."):** the camera at y = -0.8 is inside a wall. The 1.3 s of black hides the shot's whole point, the lamplight in the door gap. Move the camera into the hall in front of her door, for example y = 0.2 to 0.5.

   Afterwards, check that no frame anywhere in the preview has a mean luma under about 50/255.

## Nice-to-have
- Preflight note 9: L35 and L57 both say "I know you're in the house." It reads as a deliberate callback. Leave it.
