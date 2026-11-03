# ep47-fitting-room: standards, round 7

Verdict: approve

## Must-fix

None.

## Checked, pass

- **r6 must-fix:** package.json `title` is now "My Uncle NEVER Lies. He's Covered 🏷️": a statement, 6 words, one CAPS word, one end emoji, no spoiler, and no queued title opens with "My" (hard rule 5).
- **Flashing:** preflight PASS on the re-drawn preview (3965 frames). Red is now 0 (it was 1 at 0.73 s), so the coat change cleared it. 1-frame: 1 flash, 3 changes. 3-frame: 2 flashes, 5 changes at 14.07 s, extended run 1.67 s from 10.97 s. Bright cuts max 2 a second. Description line: 0:01 to 2:10.
- **Kids:** the opening shoppers, the cafe man in the red cap, the grey-haired woman, Uncle and the narrator all read as adults. The suit leans in behind the narrator (about 1:36) but nobody young is in peril or shown hurt.
- **Fiction and lettering:** the tags carry only the hook glyph. The arcade, cafe, shop and flat show no signs, words or cropped lettering. The dark green Uncle wall is plain.
- **IP:** faces and outfits are ours. The red cap is a plain generic cap, not a catalogue item. No game name in the title, description or pin.
- **Package:** the description says "It's made up.", sets up without the twist, and uses no banned word. The pin ("Comment TAG if you'd be covered by now.") follows the reset format. `made_for_kids` is false. Hard rule 8 passes in the title, description, pin and spoken lines.
- **Intersections:** none seen in the tag pops, the Uncle close-ups or the suit beats.

## Nice-to-have

- story.json `title` still holds the old rule line. Copy the new title in.
- Per RULES (Packaging, Hold), remove `hold` from package.json in this fix PR once the critic also approves.
- Check the 14.0 s stretch (3-frame changes 5 of 6) first on the Actions final.
