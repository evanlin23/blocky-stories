Verdict: revise

Round 5 is a look at the changed shots only, after the head-clip moves in 6e3a3cc and the flash light changes. I rendered 25 current stills (`blocky stills`, which reads the current story.json) and checked them at 300 px wide.

## Shot by shot
- S09 11.5 s: me and Jonah are both lit and both faces read. Pass.
- S19/S20 23.8 and 24.8 s: the dark window and the 1:01 timer still read after the darkening. Pass.
- S22 26.4 and 27.2 s: towelman and basketlady leave cleanly and nothing overlaps. Pass.
- S36-S45 (44.8, 47.6, 50.3, 53.7 s): eye contact, the creature's face and the arm wrestle all hold. At 50.3 s the top of the frame crops Jonah's head, but the old preview cropped it too. Pass.
- S46-S52 (55.2 to 61.6 s): the climax is darker but not murky. The 7:30 timer, the open door with its ring, the shut door and the dark window all read. Pass.
- **S54 62.9-64.3 s ("and spent / I'd BOUGHT"): broken.** The seated pair moved from y 2.95 to 2.6, but the S54 camera stayed at y 2.0 and 1.9. Their backs now sit 0.6 m from the lens and fill the frame with black and green. The 7:29 timer is hidden for about 1 s and shows only half-covered at 64.1 s. On a phone this is a black screen with captions on it.
- S53, S55-S57 (62.4, 65.0, 66.9 s): the face-cam follows. The faces, the 7:29 and 2:14 timers and the ring all read. Pass.
- S59 69.0 s: faces are washed out and the tops of the heads are cropped. Both were the same in the old preview. Pass.
- S62 72.1 s: the hug reads, both faces are visible and nothing clips. Pass.

## Scores
- Changed shots read on a phone: 6. S54 fails, every other changed shot passes.
- Climax readability: 7.
- Framing and eye contact: 6. S54 fails, the rest hold.

## Must-fix
1. S54 (L43), 62.9-64.3 s. Move the camera back by the same 0.35 m the pair moved: cam key 0 `[3.15, 2.0, 0.55]` becomes `[3.15, 1.65, 0.55]`, and key 1 `[3.15, 1.9, 0.6]` becomes `[3.15, 1.55, 0.6]`. Keep the look target. Then render a still at 63.6 s and check that the 7:29 timer is clear between the two heads. Run clipcheck again.
