"""Writes lines.json from the compact chunk table below (captions with CAPS key words; the spoken text is
derived: CAPS go lower case, sentence starts and names are capitalised again)."""
import json
import re
from pathlib import Path

T = {
"L01": ["Never let", "a man with", "no CLOCK", "near someone", "you LOVE."],
"L02": ["Every clock", "counts down to", "your next HUG."],
"L03": ["So the ferry", "arrivals are a", "field of ZEROS."],
"L04": ["The ticket man's", "dial says YEARS.", "He likes it", "that WAY."],
"L05": ["On a first", "date, you both", "sneak a", "look UP."],
"L06": ["These two both", "read four HOURS.", "Both went RED."],
"L07": ["Worst is two", "strangers hitting", "zero TOGETHER."],
"L08": ["They look everywhere", "except at", "each OTHER."],
"L09": ["And then", "there's ME."],
"L10": ["My dial", "is BLANK.", "Not even", "a ZERO."],
"L11": ["That suits me", "fine. I don't", "do HUGS."],
"L12": ["My girlfriend Lena", "keeps bees", "on the HILL."],
"L13": ["In two years,", "I've never set", "foot in", "the YARD."],
"L14": ["Her dial has", "always said MONTHS."],
"L15": ["Every evening I", "walk her to", "the gate, and", "I WAVE."],
"L16": ["On Monday,", "as I waved,", "her dial dropped", "to a few", "SECONDS."],
"L17": ["Then it jumped", "straight back", "to MONTHS.", "I blamed", "the BEES."],
"L18": ["I said I'd", "help carry honey", "down on SATURDAY.", "From the gate,", "obviously."],
"L19": ["On Wednesday,", "her dial started", "counting HOURS."],
"L20": ["Seventy-two. And I", "had no idea", "who was COMING."],
"L21": ["She worked the", "hives all afternoon.", "I watched", "from the GATE."],
"L22": ["Seventy.", "Then SIXTY-six."],
"L23": ["Then I saw", "someone in the", "last row", "of HIVES."],
"L24": ["A man in", "honey gold and", "smoke GREY,", "perfectly STILL."],
"L25": ["Between his boots", "and the grass", "was a gap,", "a hand WIDE."],
"L26": ["His feet weren't", "touching the GROUND."],
"L27": ["And over his", "head there was", "no dial", "at ALL."],
"L28": ["I called", "to Lena.", "When she", "turned round,", "the row", "was EMPTY."],
"L29": ["Thursday, she was", "on FORTY-eight."],
"L30": ["And he", "was back.", "Two hives NEARER."],
"L31": ["The bees circled", "him slowly, the", "way they circle", "a HIVE."],
"L32": ["Friday, she was", "down to TWENTY-four."],
"L33": ["He was at", "the shed inside", "the gate, beside", "the VEILS."],
"L34": ["Two veils hang", "there on", "wooden HOOKS."],
"L35": ["One is Lena's.", "The other", "is mine.", "I've never", "WORN it."],
"L36": ["She hung", "it up", "the week", "we MET."],
"L37": ["He stood by", "my veil all", "evening, a hand", "above the GRASS."],
"L38": ["Somebody was going", "to hug Lena", "at noon on", "Saturday. I thought", "it would", "be HIM."],
"L39": ["Saturday was the", "harvest. I waited", "at the gate", "with empty JARS."],
"L40": ["Lena lit", "the smoker,", "and the yard", "went soft", "and GREY."],
"L41": ["Her dial", "said ONE minute."],
"L42": ["I couldn't", "see her.", "I couldn't see", "the HIVES."],
"L43": ["I waved the", "smoke away", "from my FACE."],
"L44": ["And he was", "RIGHT there."],
"L45": ["Floating in the", "gateway, his face", "a hand above", "mine, looking DOWN."],
"L46": ["Bees went round", "his head in", "a slow RING."],
"L47": ["Behind him, her", "dial said", "TWENTY seconds."],
"L48": ["And I thought", "about the RULE."],
"L49": ["The dial tells", "you WHEN.", "It never tells", "you WHO."],
"L50": ["Somebody was going", "to hug Lena", "in twenty seconds,", "whatever I DID."],
"L51": ["So I decided", "it was going", "to be ME."],
"L52": ["I stepped past", "him, grabbed my", "veil off its", "HOOK and RAN."],
"L53": ["I pulled it", "on as I", "ran, for the", "first time EVER."],
"L54": ["Her dial said", "three. Two. ONE."],
"L55": ["I hugged her", "so hard our", "veils BUMPED."],
"L56": ["Her dial hit", "zero and glowed", "slow GOLD."],
"L57": ["And over MY", "head, something", "lit up."],
"L58": ["Numbers. For the", "first time in", "my LIFE."],
"L59": ["When the smoke", "cleared, the gateway", "was EMPTY."],
"L60": ["Then I understood", "Monday at", "the GATE."],
"L61": ["Every time I", "nearly hugged her", "goodbye, it had", "dropped to SECONDS."],
"L62": ["And every time", "I only waved,", "it jumped back", "to MONTHS."],
"L63": ["All this time,", "it had been", "counting", "down to ME."],
"L64": ["To every time", "I nearly", "did IT."],
"L65": ["And mine was", "blank because it", "was waiting for", "me to DECIDE."],
"L66": ["Lena laughed so", "much her veil", "steamed UP."],
"L67": ["Now both veils", "come off their", "hooks every MORNING."],
"L68": ["At the gate", "now, I", "hug FIRST."],
"L69": ["In this world,", "the CLOCK over", "my head counts", "down to my", "next HUG."],
"L70": ["Mine has", "NUMBERS now."],
}
NAMES = {"i": "I", "i've": "I've", "i'd": "I'd", "i'm": "I'm", "lena": "Lena", "lena's": "Lena's",
         "monday": "Monday", "wednesday": "Wednesday", "thursday": "Thursday", "friday": "Friday",
         "saturday": "Saturday"}


def spoken(chunks):
    toks = []
    for c in chunks:
        toks += c.split()
    out, start = [], True
    for w in toks:
        core = re.sub(r"[^A-Za-z'\-]", "", w)
        low = w
        if core.isupper() and len(core) > 1 or core.upper() == core and "-" in core and core.split("-")[0].isupper():
            low = w.lower() if not re.search(r"[a-z]", w) else w
        if re.match(r"^[A-Z]{2,}-[a-z]", w):   # FORTY-eight -> forty-eight
            low = w.split("-")[0].lower() + "-" + w.split("-", 1)[1]
        if re.match(r"^[A-Z]{2,}[\.,]?$", w) or re.match(r"^[A-Z]{2,}-[A-Za-z]+[\.,]?$", w):
            low = w.lower()
        key = re.sub(r"[^a-z']", "", low.lower())
        if key in NAMES:
            low = low.replace(key, NAMES[key]) if low.lower().startswith(key) else low
            low = NAMES[key] + low[len(key):] if low.lower().startswith(key) else low
        if start and low[:1].isalpha():
            low = low[0].upper() + low[1:]
        start = bool(re.search(r"[.!?]$", low))
        out.append(low)
    # split back into the chunk sizes
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
for l in lines[:25]:
    print(l["id"], [c[1] for c in l["chunks"]])
