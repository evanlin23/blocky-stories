# floor-thirteen, round 6, standards (new opening and package)

Verdict: revise

Checked: script.md, story.json, package.json, the preview (quarter-res, every 4th drawing) 0-4 s sheet and contact sheet, frames at 0, 0.5, 1.0, 51.6 and 92.5 s, preflight, every queued title, and the voice.py change.

1. **Fiction:** pass. The panel buttons are blank, the only set text is "13" and the tag's "12".
2. **Kids and mature themes:** pass. Adults only. Grandad's forgetting stays gentle, and nobody is hurt.
3. **IP:** pass.
4. **Originality:** must-fix, title only. The story itself still differs from every queued one.
5. **Flashing:** preview PASS, still on the bar: 3-frame 3 flashes and 6 changes at 26.6 s (bright landing to dark car), 1-frame 2 at 67.1 s. The loop seam (dark Attendant to the lit panel) reads 1. Watch both on Actions.
6. **Package:** must-fix, the hold key.

## Must-fixes
1. **package.json `title`:** "My Elevator Pressed 13 By ITSELF 🛗" sits next to ep62's "The Elevator Mirror Shows FIVE 🛗". Both have Elevator as the second word, a number hook and the same emoji, and both films are elevator rides. In the channel grid that reads as templated. It also says the elevator "pressed", while L01 and the first frame say the button "lights up". Change it to **"My 13 Button Lit Up By ITSELF 🔘"**. No other queued title starts "My", "Never" or "If the", and none uses 🔘.
2. **package.json:** delete the `"hold"` key in this PR once fix 1 is in.

## Notes
- voice.py "passed"/"past" and "press"/"pressed" only forgive mismatches in the ASR check, and films don't change. One story is at risk: ep34 L14 "You press the button" would now pass if it were heard as "pressed". That's acceptable.
- ep31 (Dad forgets me every morning) shares this ending shape. It's dropped from the queue, so keep it that way or keep it far from this one.

## Nice-to-haves
- In the description, "Keys, birthdays" should be "Keys, anniversaries" (L03 is an anniversary).
- `cover_s` 51.6 has the caption "of the DOORS.". About 53 s on the lit tag would tie better to the title.
