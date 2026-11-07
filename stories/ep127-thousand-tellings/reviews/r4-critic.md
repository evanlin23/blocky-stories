# ep127-thousand-tellings, critic r4 (staging fix, S84-S86 only)

Checked every frame 71.0-73.5 s of the preview at 390 px, and full-size crops at 71.75, 72.05, 72.3, 72.4, 72.5, 72.6, 72.7, 72.85 s. Fixed: the door swings open 71.43-71.8 s, before he moves (the walk starts at 71.87 s from y -7.4). The door hit lands at the 71.1 s cut, about 0.3 s before the leaf visibly moves, which still reads as one event. He walks now, with legs cycling (3 m over 1.07 s, brisk but not a slide). "So on the last night, / I went in / to STOP him." reads, and the face stays whole with eyes clear in the frame through the push. S86 (Grandpa, 72.93 s on) is unchanged and clean.

Still broken: he passes through the leaf and the right jamb. At -75 degrees the leaf (hinged at x 3.42, y -6.0) reaches in to its free edge at about (3.15, -5.0). His walk line is x 2.9, and the rig's shoulder span is about 1.33 m, so his screen-left arm reaches x of about 3.57. The doorway is only 1.1 m (2.35-3.45). In the crops at 72.35-72.75 s, his screen-left arm is drawn in front of the jamb and the leaf's hinge side while the leaf's free stile cuts across his shoulder and chest. That is a body through glass and frame for about 12 frames at full speed. Preflight lists no clip row, because it checks heads only.

Verdict: revise

Must-fix
1. S85, 72.35-72.75 s (L46.2 to L47, `me` walk plus the `door` cue). Clear the leaf and the jamb:
   - Open the door to about -100 degrees, flat to the wall, so it frees x < 3.37.
   - Make him fit the 1.1 m opening. Either yaw him about 30 degrees side-on while y is between -6.4 and -4.9, or move the walk line to x 2.8 and narrow him (body_width about 0.8) for this shot only.
   - Re-pull 72.3-72.8 s and confirm that no arm overlaps the jamb or the leaf.
