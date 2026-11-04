# ep52-ferry-crossing: standards, round 5

Verdict: approve

r4 must-fixes, checked:
1. script.md matches the build. I compared all 70 spoken lines against story.json's chunks and found no differences. L01 and L02 are the built `if` warning in the Rule bullet, "First line" and the line list. L13, L42, L57 and L58 match.
2. L36 is "outside my PLACE / in TOWN".
3. cover_s is 103.5 (S69). The lit Shrug turns its face to Gran with its teeth showing, and it reads clearly with no hump filling the frame.
4. HANDOFF.md is left to the merge commit, as briefed.
- Nice-to-have done: `premise` says "harbor". "harbour" is left only in a shot `what` note and set.py comments, which viewers never see.

Re-checked: fiction passes (no set text, the phone screen is blank, no signs). Kids and mature themes pass (all adults, and the Shrug never touches Gran). IP passes. Originality passes against the queue and the earlier stories. `opening: if` matches L01. The queue's only other `if` is floor-thirteen, so ep52 only needs to sit away from it and from nothing else.

Flash: the preview fails the house bar with 8 flashes a second at 102.3 to 104 s (S69, L51 "and leans IN closer"). Full-rate frames show a repeating 4-frame pattern. One frame is framed wider and brighter (mean luma about 106, more of the white ceiling strips), then three frames are tighter and darker (about 97), with about 35 to 40% of the area changing at each switch. That's the preview's drawing grid (1 drawing held against 3), not a light in the scene. The camera doesn't jump in the story and nothing in it flickers. It isn't a must-fix, but the proof's flash JSON has to show S69 under the bar. If it still flags there, the fix is to draw S69 on ones (`"step": 1`) or slow the lean, not to change the light.

Nice-to-haves:
- check warns that the glitch at L35+0.3/+0.9 is above -24 dB. Keep it quieter.
- The "the way" caption is up for under 0.2 s.
