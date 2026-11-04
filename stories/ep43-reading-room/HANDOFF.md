# ep43-reading-room: dropped again (2026-11-04)

Re-imagined from revival triage pick 3 ("Days since you last laughed", the Negative made of every swallowed laugh). The script and package were written (Opus writer; cold viewer 7/10, then one fix round). The build reached phase 1 (set, story.json, voice). No preview, no reviews, no PR.

**Why it was dropped:** the creature test still failed all three tries with the Opus critic at phone size (RULES "The creature", the three-try limit):
1. Thin downturned arc on a flat black block face: "a sad cartoon face, not a monster" (fail).
2. Whole face hung upside down on a too-long neck: "a dark penguin or bean blob tumbling sideways with a cartoon face", 3/10. The critic: "an upside-down R6 face loses its face read at phone size."
3. Upright head on a too-tall box body (creature-playbook pass zone): "a grumpy cartoon mascot... dot eyes and the downturned crescent make a sulky emoji face", 4/10.

**Root cause:** plant 2, "its mouth is an upside-down smile", needs a drawn mouth shape, and creature-playbook rules 8 and 15 (no grin, no drawn face) say a drawn mouth shape reads cartoonish in this engine. On a block face, any upside-down grin reads as a frown or a sulk. "Printed in reverse" also never read at phone size.

**To revive it:** a writer needs a new creature concept that carries no drawn face expression: for example, drop plant 2 and show the swallowed laughs some other way (a shape behind frosted dome glass, hands pressed over a face that isn't there, or the outline of a crowd's hands). The rule, the reveal, the joke climax and the street and dome sets are sound and reusable. Sunk cost never counts: rebuild only if the new creature passes a test still first.

The builds so far are on branch `claude/revival-ep43` (set.py, generator, story.json, script.md).
