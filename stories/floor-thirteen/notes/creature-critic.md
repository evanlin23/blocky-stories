---
role: critic
round: creature-test
verdict: revise
scary: 3/10
readability: 3/10
---

# ep14-floor-thirteen: critic on the creature test (v8)

I looked at `review/creature-test.png` at 360 px and at full size, at `creature-test-phone.png`, and at v1 to v8 side by side. To find out what's hidden, I rendered scratch look frames of the same set without the cast and with other poses and cameras. They're in the scratchpad, not the repo: `/tmp/claude-0/-home-user-content/b641d2f4-4361-513a-b129-7ef6b9d31a8a/scratchpad/critic/`.

## Cold read (first half second, phone)

An open jewellery box (or a speaker cabinet, or a keypad toy) with nine glowing rings sits in a lit window behind two sofa cushions, with a "13" above it. It isn't a figure. It's neutral and a little silly. Only the dark and the "13" make it eerie.

- **Reads:** the 3x3 lift buttons, the hotter centre button, the "13", the caption.
- **Doesn't read:**
  - **The uniform:** below the panel the jacket measures median luma 0 (p90 21).
  - **The gloves and the too-long arms:** they aren't in the picture. In the no-cast render they hang to the floor behind Mr. Okafor's shoulders.
  - **The stoop:** a 54-degree bow seen from inside the car foreshortens into a box on a pedestal. It also puts the face at about 1.7 m, ordinary head height, so the 2.42 m height is lost.
  - **The doors closing on it:** the leaves are unlit and our heads cover them, so the lit gap reads as a TV or window.
  - **The two of us:** we're seen from above and behind. His head is a dark armrest, his shoulders are two olive cushions (median 41, brighter than the monster) and my hood is a purple seat back.
- **The head:** the cap is a slab exactly as wide as the head, on top of a brass outer frame. That's the lid and rim of a box.

Without the cast, the body is all there: the jacket, eight brass buttons, shoulder boards and the long sleeves. **The concept works. This frame hides it.**

## Scores

| | Score | Why |
|---|---|---|
| Scary | 3 | It reads as an object, so there's nothing to fear. Nine dim grey rings with dark middles read as speaker cones or keys, not a wall of cold light a foot from my face. |
| Readability | 3 | The panel and the "13" read instantly. Of the uniform, gloves, arms, stoop, doors and cast, none reads. |

**Grid:** keep 3x3. The 2x2 reads as a socket or a die, and the 3x3 buttons don't blur. Both grids still read as a device in this frame, though, so the brief's kill line ("toy or robot in both grids after two passes") is arguably met. The redesign it prescribes (more human-shaped, the panel set into a real block head, the buttons recessed into darkness) is fixes 1 to 4 below. I'd run that inside row 1, not kill. Producer's call.

## Changes, in priority order

1. **Clear the gap: camera and cast.**
   - Put the camera on the car's centre line at the back wall, at 1.5 m (shoulder height, not 1.9), aimed about 1.6 m up in the doorway, 19 to 20 mm. Keep the "13" in the top 10% of the frame.
   - Block both of us against the side walls so neither overlaps the 0.8 m gap anywhere from header to sill. My hood is side-on at the right edge, over the right jamb and floor panel. He's at the left edge, cropped, at most about 20% of the frame width.
   - Re-probe the cast: my rough placements hit the panel and the wall.

2. **Bow 30 degrees, not 54. Fold the gloves.**
   - Probed in scratch: `pos [0, -1.50]`, `lean 0`, `bend 30`, `head [8, 0, 0]`, `fold 1.0`. This is `v/p6b.json` in my scratch folder.
   - The header crops its cap, so the doorway is visibly too short for it, and all nine buttons sit just under the header.
   - The legs show. The arms hang beside the legs and the gloves meet right over left below its knees. v8's `fold 0` breaks the brief's "always folded" rule and drops the gloves to the floor, where they read as white boots.
   - The Attendant's only probe overlaps are its sleeves against the car leaves, which is the bump itself. Stop the leaves 1 cm short of them, as v8 does.

3. **Light the monster, not us.**
   - Re-aim the 70 W `panel_key` from the head (which lights itself) to the folded gloves. It already sits at glove height. Target about 150 to 170 luma, the brightest thing that doesn't glow, clear of the caption band.
   - Add two narrow cold rims from 13's side (0.2 m area lights, about 45 W, at x = ±0.75 m, 0.6 m past the sill, 1.5 m up) aimed down each sleeve. The outline then runs shoulder board, sleeve, cuff, glove, and the length reads in silhouette.
   - Give the brass buttons and piping a glossy-visible source so the 2x4 buttons ping down the jacket. Avoid a diffuse blob on the chest: 40 W under the chin read as a torch on a shirt.
   - No fill on us. Only its cold glow rims the top and the inner side of each head. Our tops stay under about 30 luma.

4. **Make the head a head, not a box with a lid.**
   - Deepen the lacquer housing from 0.14 m to about 0.4 m, the cast's head depth.
   - Set the brass frame and plate about 8 cm back inside a 5 cm black lacquer lip (brow, cheeks, chin), so the nine lights sit in a black socket and the outline is black on black.
   - Add a short wool neck block, about 7 cm, between the collar and the head.
   - Rebuild the cap as a cap. The crown flares about 10 cm wider than the head on each side, the brass band sits at head width, and a glossy visor about 18 cm deep angles 25 degrees down over the top row, so the top row lights its underside.
   - Unchanged: 0.54 m panel, 3x3, no marks.
   - Re-probe the header: a deeper head sits further forward.

5. **Make the doors visibly shut on it.** Light each car leaf's leading edge with a thin cold line from 13's side, or use a brighter satin `edge` strip, so two vertical lines meet its sleeves at the gap. Right now the leaves are black bands, and only motion would tell you they're doors.

Check after these: the eye still the hottest thing, nothing clipping, no face reflected in the lacquer or the glass, and the 3x3 count readable with all nine lit.

## Pass 2 (v12): pass, with ride-along fixes for the build

**Scary 5/10, readability 6/10. Verdict: pass.** The creature design is settled: the socket head, the cap, the uniform, the 40-degree bow and the light rig. What's left is tuning that can ride into the build without another critic round. I re-checked my own probes in the scratchpad (`critic/out/`: `noarms`, `q1` to `q4`, `fw300`, `g1`).

**First half second (360 px):** a tall black figure fills a lift doorway, with nine cold lights for a face, long arms down to white hands, and a "13" over it. It's eerie, not silly. It no longer reads as a jewellery box or a speaker.
- **The glance that can still misfire:** the two arms meeting at a point on two cubes can flash as a black funnel ending in a sugar cube.
- **What reads:** the figure, the black jacket with its brass buttons, the gloves, the face set back in darkness, the door edges and the "13". The caption is clear of the face.
- **What doesn't:**
  - **The stoop:** it reads as standing, which is fine. The header crop sells its height.
  - **The legs:** with the arms hidden, the legs sit right behind the V. From this axis the crossed arms always hide them, so don't chase them.
  - **The two of us:** we're slivers, so the frame gives no human scale and nobody is in danger.

**Why scary stops at 5:** it's dread with nobody near it, the face tips 38 degrees down at the floor in front of us rather than at us, and the cube gloves look like toy parts. Motion and silence have to carry the rest. If the preview's scary is still 5 or below, the brief's kill line applies, and the fix then is the bump and the sound, not the creature.

**Ride-alongs, in priority order:**
1. **Gloves longer than they are wide.**
   - Change: `GLOVE_L` 0.62 → about 0.95 units and glove width 0.68 → about 0.5 units. The arm stays 3.6 in total.
   - Why: a 0.21 x 0.23 m glove is a cube, so it reads as a die or a sugar cube. A long glove reads as a hand hanging from the cuff.
   - Keep the right glove in front and lit, with the left one a step darker behind it.
   - Tested in `critic/out/g1.png`: that one change turns the "two white blocks" and most of the "wedge" into hands.
2. **Light 13's floor behind the gloves.**
   - Add a cold area light of about 200 W, 0.8 m across, at (0, SILL_Y - 1.3, 2.3), aimed at the foot of 13's back wall.
   - That puts lit carpet behind and beside the gloves, so they hang in front of something rather than sit on a black floor.
3. **Kill the soft hot halo on the right leaf and jamb, beside "DOORWAY."**
   - It reaches luma 195 and is the third-brightest patch in the frame, so it pulls the eye off the face.
   - It's the right sleeve rim spilling onto the leaf. Tighten its spread or link it off the jamb, and keep only the thin edge line.
   - Turn Mr. Okafor a few degrees further so his tie isn't a stray red stripe down the left edge.
4. **Optional, and worth it if it comes clean: lift the face toward us.**
   - Change: `bend 44`, `head [-18, 0, 0]`. The probe found 0 overlaps.
   - The face then tips about 26 degrees down instead of 38, so it looks at us rather than the floor, and the visor's underside draws a cap brim under the header.
   - **The catch:** it puts a glint in the top-middle glass at luma 255, hotter than the eye (244). That's a second eye.
   - Only take it if `face_peak` stops showing in the glass (glossy off, or moved) and the eye stays the hottest thing.
5. **Scale and danger come from the cut, not this frame.**
   - L57 ("a FOOT from my FACE") needs its own insert: the lit panel filling the upper half over the back of my dark, cold-rimmed hood.
   - Keep the bump on the car's centre axis. From here the 20 cm between the leaves and its sleeves can't be seen, and the "stop at 0.80 m as if they hit it" cheat holds. A side angle would give it away.

Before the build locks the look, check two things: the eye is still the hottest pixel group, and all nine buttons still count as nine with nothing reflected in the glass.
