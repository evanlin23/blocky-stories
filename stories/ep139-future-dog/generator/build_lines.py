"""One-off helper that wrote lines.json from the script's narration (kept so the words stay reproducible)."""
import json, re
from pathlib import Path
SRC = """
L01: On your thirtieth, / it's YOU / on the phone, / from LATER. / Mine only asked / for my DOG.
L02: You get ONE call. / EVER.
L03: My neighbor's / told her / to stop cutting / her own BANGS.
L04: My buddy Sam's / said, / don't buy / the red CAR. / He did. / It's a LEMON.
L05: Mine rang / at SEVEN.
L07: "ACHOO."
L08: That's Noodle, / my old BEAGLE.
L09: He sneezes / every time / anyone says SEVEN.
L10: My big brother Theo / taught him THAT.
L11: Theo's lived / across the ocean / for five YEARS.
L12: We text. / Mostly / about the DOG.
L13: I answered, / and future me / didn't even say HI.
L14: He said, / "Put me on SPEAKER. / Is Noodle THERE?"
L16: So Noodle hopped up / by the PHONE.
L17: And future me / said two words, / really SLOWLY.
L18: "GATE."
L19: "Seven-FORTY." / "ACHOO."
L21: "Gate. / Seven-forty." / "ACHOO."
L22: For six whole MINUTES.
L23: Then, / CLICK.
L24: I asked Noodle / what it MEANT.
L25: He just turned / and looked / at the GATE.
L26: All night, / he lay / right by it,
L27: SNIFFING / under the GATE.
L28: At 7:38 / the next morning, / he was WHINING.
L29: At 7:39, / he nosed / the latch OPEN. / "ACHOO."
L30: At 7:40, / he RAN.
L31: Me behind him, / on the leash, / in my SOCKS.
L32: Three streets / to a moving VAN.
L33: And a man / by the ramp / turned around / and said my NAME.
L34: It was THEO.
L35: He'd been back / a whole WEEK.
L37: SEVEN nights, / he'd texted me / and deleted it.
L38: "ACHOO."
L40: Then Noodle / jumped into his ARMS.
L41: And Theo whispered, / "SEVEN."
L42: "ACHOO."
L43: And we both LAUGHED, / like nobody / had ever been AWAY.
L46: Now every morning / at seven-forty, / we walk to Theo's / for COFFEE.
L48: "ACHOO."
L44: Future me knew / I'd overthink it / for a WEEK. / So he told / the one of us / who never DOES.
L49: And I already know / who I'll ask for / when it's MY call.
"""
def spoken(c):
    s = c.lower().replace('"', '')
    s = s.replace("achoo", "achoo").replace("7:38", "seven thirty-eight").replace("7:39", "seven thirty-nine").replace("7:40", "seven forty")
    s = s.replace("seven-forty", "seven forty").replace("thirtieth", "thirtieth")
    return s.strip()
out = []
for ln in SRC.strip().splitlines():
    lid, txt = ln.split(": ", 1)
    ch = [[c.strip(), spoken(c.strip())] for c in txt.split(" / ")]
    out.append({"id": lid, "who": "narrator", "chunks": ch})
Path(__file__).with_name("lines.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
print(len(out), "lines")
