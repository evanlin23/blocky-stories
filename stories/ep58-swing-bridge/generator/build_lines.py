"""Writes lines.json from the compact chunk table below (captions with CAPS key words; the spoken text is
derived: CAPS go lower case, sentence starts and names are capitalised again)."""
import json
import re
from pathlib import Path

T = {
"L01": ["If your hands", "stop GLOWING,", "stay off the", "old BRIDGE."],
"L01b": ["Dark hands mean", "nobody NEEDS you."],
"L02": ["The doctor hid", "at the back", "of the CINEMA."],
"L03": ["Her hands lit", "up the whole", "ROW."],
"L04": ["His dog's waiting", "at HOME,", "so he glows", "all through WORK."],
"L05": ["After a fight,", "you both glow,", "and you both", "pretend you DON'T."],
"L06": ["Pockets don't help.", "The light gets", "OUT."],
"L07": ["And then", "there's ME."],
"L08": ["My hands have", "never glowed.", "Not that", "I've SEEN."],
"L08b": ["And something on", "the old bridge", "has hands that", "never glow", "at ALL."],
"L09": ["My wife, Ada,", "is the strong", "one, so nobody", "needs me.", "And I don't", "need ANYBODY."],
"L10": ["But my wife's", "dad, Emrys,", "was going DARK."],
"L11": ["They'd bolted his", "old swing bridge", "SHUT, and nothing", "needed him ANYMORE."],
"L12": ["Ada said if", "his hands went", "out, he'd never", "leave that CABIN."],
"L13": ["So she asked", "me to sit", "with him in", "the EVENINGS."],
"L14": ["He still calls", "me the LODGER."],
"L15": ["Every evening he", "sat in the", "cabin by", "the wheel,", "waiting for BOATS."],
"L16": ["And week by", "week, his hands", "got DIMMER."],
"L17": ["By October, you", "could only see", "them in", "the DARK."],
"L19": ["He always had", "two mugs out", "before I got", "THERE."],
"L20": ["At dusk, he", "still raised one", "hand to the", "empty RIVER."],
"L21": ["Walking home, I", "kept my hands", "in my POCKETS.", "It was COLD."],
"L22": ["Then two wet", "handprints appeared on", "the rail by", "his WINDOW."],
"L23": ["And the whole", "rail CREAKED", "in the FOG."],
"L24": ["On Thursday, the", "cabin was DARK.", "The door was", "OPEN."],
"L25": ["Emrys wasn't", "THERE."],
"L26": ["His cap hung", "on the wheel.", "His mug was", "still WARM."],
"L27": ["And wet handprints", "ran along the", "rail, all the", "way to the", "far BANK."],
"L28": ["I searched the", "bank till midnight.", "Nobody had", "SEEN him."],
"L29": ["He came home", "at breakfast, mud", "up to his", "KNEES."],
"L30": ["He'd walked to", "the new bridge", "to ask if", "they needed", "a HAND."],
"L31": ["They DIDN'T."],
"L32": ["That night his", "hands were nearly", "DARK."],
"L33": ["He wouldn't leave", "the cabin, so", "NEITHER did I."],
"L34": ["On Monday, something", "stood on the", "far BANK."],
"L35": ["Just a shape", "in the fog,", "leaning on the", "RAIL."],
"L36": ["On Tuesday, its", "hands were halfway", "ACROSS."],
"L37": ["On Wednesday, they", "were at OUR", "end, under the", "WINDOW."],
"L38": ["Its hands didn't", "glow at ALL."],
"L39": ["On Thursday, the", "stove burned down,", "and the lamp", "went LOW."],
"L40": ["And it was", "at the window,", "with US."],
"L41": ["It had come", "across. Its hands", "were on the", "far BANK."],
"L42": ["An ordinary man", "in an ochre", "WAISTCOAT."],
"L43": ["But its arms", "were as long", "as the BRIDGE."],
"L44": ["Back along the", "rail, all the", "way to its", "HANDS."],
"L45": ["And slowly, it", "leaned in at", "the window,", "face to face", "with ME."],
"L46": ["Emrys stared at", "his hands. They", "were DARK."],
"L46b": ["It comes", "for the ones", "nobody NEEDS."],
"L47": ["Then I saw", "MINE."],
"L48": ["The stove was", "out, and my", "hands were GLOWING."],
"L49": ["Faintly. And they'd", "been glowing for", "MONTHS."],
"L50": ["In my POCKETS.", "Every walk HOME."],
"L51": ["Somebody needed me.", "It was HIM."],
"L52": ["Two mugs out,", "every night, before", "I got THERE."],
"L53": ["I'd thought need", "had to be", "big, like a", "boat or", "a BRIDGE."],
"L54": ["But the rule", "just says SOMEBODY.", "One is ENOUGH."],
"L55": ["So I told", "him I didn't", "know how to", "be in", "this FAMILY."],
"L56": ["And that I", "needed him to", "show ME."],
"L57": ["His hands came", "up slowly, like", "a lamp turned", "UP."],
"L58": ["Between us, our", "hands lit the", "whole cabin.", "The window was", "EMPTY."],
"L59": ["The next evening,", "I crossed the", "old bridge at", "DUSK."],
"L60": ["Emrys raised one", "bright hand at", "the cabin WINDOW."],
"L61": ["The wave he", "gave every boat", "for forty-one", "YEARS."],
"L62": ["And he called", "me by", "my NAME."],
"L64": ["At three this", "morning, my hands", "woke me, GLOWING."],
"L65": ["Everyone who needs", "me was asleep.", "But two dull,", "flat hands lay", "on our WINDOWSILL."],
"L66": ["Nobody has ever", "needed it.", "Tonight, it", "needs ME."],
}
NAMES = {"i": "I", "i've": "I've", "i'd": "I'd", "i'm": "I'm", "ada": "Ada", "ada's": "Ada's", "emrys": "Emrys",
         "monday": "Monday", "wednesday": "Wednesday", "thursday": "Thursday", "tuesday": "Tuesday", "october": "October",
         "he'd": "He'd"}


def spoken(chunks):
    toks = []
    for c in chunks:
        toks += c.split()
    out, start = [], True
    for w in toks:
        core = re.sub(r"[^A-Za-z'\-]", "", w)
        low = w
        if len(core) > 1 and core.isupper():
            low = w.lower()
        if re.match(r"^[A-Z]{2,}-[a-z]", w):
            low = w.split("-")[0].lower() + "-" + w.split("-", 1)[1]
        key = re.sub(r"[^a-z']", "", low.lower())
        if key in NAMES and key != "he'd":
            i = low.lower().index(key)
            low = low[:i] + NAMES[key] + low[i + len(key):]
        if start and low[:1].isalpha():
            low = low[0].upper() + low[1:]
        start = bool(re.search(r"[.!?]$", low))
        out.append(low)
    res, i = [], 0
    for c in chunks:
        n = len(c.split())
        res.append(" ".join(out[i:i + n]))
        i += n
    return res


lines = []
for lid, ch in T.items():
    sp = spoken(ch)
    lines.append({"id": lid, "who": "narrator", "chunks": [[c, s] for c, s in zip(ch, sp)]})
(Path(__file__).parent / "lines.json").write_text(json.dumps(lines, indent=1, ensure_ascii=False) + "\n")
for l in lines:
    print(l["id"], " | ".join(c[1] for c in l["chunks"]))
