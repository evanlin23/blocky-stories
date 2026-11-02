# ep25-plot-nine: standards, round 3

Verdict: revise

Checked: the preview contact sheet and stills sheet (quarter-res, every 4th drawing, rendered after 8dd0f91), 1 fps strips of S48 to S58 (the night and the can) and S59 to S68 (torch and Bench), `preflight` (flash PASS, 1 flash and 2 changes a second at 59.8 s, 0 red, 0 blocks), RULES.md as merged from main, and the premise and twist of every story on main and ep21 to ep35.

Pass: fiction (no set text, no real places), kids and mature themes (all adults, nobody hurt, the Bench hand reads as a prop), IP (no game names, the faces and outfits are our own), flashing, the package (66-character "In a six-week drought, ..." statement, no spoiler, "It's made up.", nothing forbidden) and rule 8. L06 is re-voiced as asked and now matches the description and script.md. The night cut is now a 1.5 s ramp from L45+1.0 and the return a 1.0 s ramp. Mean luma is 12 at 90.0 s and 58 at 91.5 s, under 1% of pixels above 200. P03's floor peaks at 221 on about 30% of the frame and ramps through the torch.

## Must-fix

1. **Originality, story.json `premise` (and `generator/make_story.py` line 440, which writes it).** It still says "when his knees give out". That's the round-2 overlap with ep26-last-skate's premise ("Pop says his knees are done"), and `check` compares premises. Replace it with the script.md wording: "In the driest spring on the hill, I take over old Mr. Carter's allotment plot when he says it's time for somebody new." Leave the rest of the premise as it is, then regenerate story.json.

## Nice-to-have

- Line 438 of the same file: story.json `title` is still "My garden was wet every morning. ...". Copy across the package title "In a six-week drought, my allotment plot is wet every single dawn."
- At 88 to 90 s, the night wide shows the hill as a near-white shape against a dark blue sky. It passes, but watch it in the final measure.
