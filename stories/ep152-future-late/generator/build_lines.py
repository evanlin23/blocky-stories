"""One-off helper that wrote lines.json from the script's narration (kept so the words stay reproducible)."""
import json
from pathlib import Path
SRC = """
L01: I'm thirty TODAY, / and future me / calls ONCE, / before MIDNIGHT. / At 11:57, / he still HADN'T.
L03: "Tick."
L04: Everybody else's / came by BREAKFAST.
L05: My cousin's / told him / to wear SUNSCREEN. / He's still RED.
L06: My best friend's / just said, / "Buy the HOUSE." / He LOVES it.
L07: My mom's kitchen / has fourteen CLOCKS.
L08: Every one / is ten minutes FAST.
L09: Because I've been late / my whole LIFE.
L10: She swears / they're RIGHT.
L11: Nobody said / what a LATE call / MEANS.
L12: 11:52. / "Tick."
L13: 11:55. / "Tick."
L14: Mom held my HAND / across the table.
L15: 11:57. / "Tick."
L16: 11:58. / "RING."
L17: I hit SPEAKER.
L18: And future me / was out of BREATH, / LAUGHING.
L19: "SORRY! / I lost TRACK / of time!"
L20: Of COURSE / I'm still LATE.
L21: But her clocks are FAST. / It was really 11:48. / TWELVE minutes to SPARE.
L22: First time / I wasn't LATE.
L23: His ONE piece of advice: / "Never tell Mom / you know about / the CLOCKS."
L24: Because he was calling / from her KITCHEN.
L25: Her clocks, / still ten minutes FAST. / Still set / for ME.
L26: When it's my turn / to call, / I'm using / HER clock.
"""
NUM = {"11:48": "eleven forty-eight", "11:52": "eleven fifty-two", "11:55": "eleven fifty-five", "11:57": "eleven fifty-seven", "11:58": "eleven fifty-eight"}


def spoken(c):
    s = c.lower().replace('"', '')
    for k, v in NUM.items():
        s = s.replace(k, v)
    return s.strip()


out = []
for ln in SRC.strip().splitlines():
    lid, txt = ln.split(": ", 1)
    out.append({"id": lid, "who": "narrator", "chunks": [[c.strip(), spoken(c.strip())] for c in txt.split(" / ")]})
Path(__file__).with_name("lines.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(len(out), "lines")
