# ep48-crazy-golf r7 critic (opening check, last look)

I checked the r6 must-fixes against preview frames at 300 px wide (0.0 to 8.0 s), then took a quick look at the rest of the contact sheet. `preflight`: 0 blocks, flash PASS, no pace or clip rows.

**r6 fixes, one by one**
1. Frame 1 shadow: **fixed.** From 0.15 s (S001) the frame is a low close-up of my trainers. The shadow is hard, black and joined to both soles, and it is darker than the jeans. At phone size it plainly reads as "a shadow stuck to my feet".
2. Hold, then the stranger cut: **fixed.** S001 holds for all of L01 (0.15 to 1.85 s). S002 cuts on "Everyone else's" (1.85 s) to a stranger's shoes with clearly nothing under them. Their own shadow, about 2 m off on the grass, is only a soft dark band. That is acceptable, because "nothing under them" next to my hard shadow is the contrast that matters, and the L02 wide at 5.3 s shows the lone shadows on the grass plainly.
3. No wide, tree, horizon or cropped head in 0 to 3 s: **fixed.** There are two close-ups and no faces to crop.
4. Pavement S003 (3.6 to 4.7 s): **fixed.** It is bright and matches the lawn, and the empty gap under the shoes is clear.
5. script.md: **fixed.** The L01, L01b and L02 shot notes match the picture.

**Hook:** 8/10. Line 1 is a personal oddity spoken over the close-up that proves it, and the rule follows by 2 s (the confess shape). Captions read at phone size and the key words are in gold.

**Rest, sanity look:** nothing new is broken. Faces are readable, the son and Dad read at a glance ("I'm his SON" at 20.6 s), and the creature shots at night and dusk are dark but legible. The ending loops back to L01.

**Note, not blocking:** drawing 0 (t = 0) shows the empty lawn with the tree and no me. The cause is that `acting.me` starts with a `pos [0, 0]` key at `at: 0`, and `position()` returns the first key at t = 0, so I stand at the world origin off-camera for that one drawing. The preview holds it for 4 frames, which is why it shows there. In the final it is 1 frame at 25% fade-in brightness (33 ms), so nobody will see it. If the builder touches the file again, delete the two `pos [0, 0]` keys at `at: 0` for `me`, so the first key is `pos [0.0, -26.2]`. The proof qa may flag it, and that one-line edit is the whole fix.

## Must-fix

None.

Verdict: approve
