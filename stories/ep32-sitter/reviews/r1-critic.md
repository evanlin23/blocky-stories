# ep32-sitter, round 1, critic

Verdict: revise

## Scores
- Hook 5: a calm line over a static shot of me. The canvas plant scripted for S01 is missing.
- Scare 6: the dips land. S43/S44 show the back of its head, so the turned head doesn't read.
- Creature 5: an eerie pine mannequin, but the joined ovals read as spectacles. The long torso barely shows.
- Twist 6: fair plants. The match between Mum's glasses and its face is the best idea here, and it's never framed.
- Lore 8: nine strokes, clear, never named.
- Warm turn 6: the Mum portrait is shown, but pine covers it (S66) and Mum is headless in S75.
- Shot variety 8.
- Faces 4: S09 reveal tiny, caption over the eyes in S46, faces cut off in S74.
- Sound 5: "not bad" is spoken twice in L66. The tail is 0.4 s.
- Captions 6: L66 is out of sync.

## Panel
- **Creepy fan:** swipes at S09 (19 s), because nothing visible sits there. "wooden guy with glasses lol"
- **Ep11 to ep13 regular:** stays and pauses on S70. "NINE marks again"
- **Scroller:** gone by 2 s, because nothing strange happens in the first shot.
- **Top comment:** "its face was her MUM's glasses??" (only if fix 5 lands)
- **Slips:** the double "not bad". In S74 Kofi's teeth read as gritted, and Mum's hand isn't up.

## Must-fix
1. L66: speak "Not bad" once. Fix the `FIX` entry in `generator/script_to_lines.py` and the L66 chunks in `story.json`, then re-voice.
2. S01 (0 to 2.1 s): close on the cross-and-ovals canvas, pushing in.
3. S09 (17.1 to 19.1 s): its head at least 1/5 of the frame width, not hidden behind easel 8.
4. S46 (84.2 to 85.6 s): eye ovals above the caption band.
5. S43/S44: a 3/4 angle showing the reversed head and the canvas together.
6. S66: pine off the portrait. S75: Mum's face in frame.
7. S74: both faces whole, Kofi smiling, Mum's hand up.
8. Tail: 0.25 s after 138.70 s.
