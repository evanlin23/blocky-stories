"""The narration (script.md L01 to L72) and how it is cut into 2 to 3 word caption chunks."""
import re

TEXT = """
In this town, every favour you owe sits on your head as a gold BLOCK.
Hold a door for someone. CLICK. A block lands on THEIR head.
It lands the second they say THANKS.
Do them a favour back, and it drops OFF. One favour, one BLOCK.
This man's street helped him move HOUSE.
Now he has to duck under the bus SHELTER.
These two neighbours have passed the same block over the fence for TEN years.
And the best man at a wedding never fits in the PHOTO.
Then there's ME.
My head is BARE. Always HAS been.
Thanks just isn't a word I SAY.
My cousin Ilan carries more blocks than the rest of the square PUT together.
We always had Saturday lunch in the stone seat under the clock ARCH.
Room for TWO.
This summer, I stopped GOING.
People had started to WHISPER about him.
They said he owed the whole town and never paid it BACK.
The first Saturday of summer, his stack was taller than the AWNINGS.
It swayed when he walked. He couldn't look UP.
People stepped around him like a PUDDLE.
I walked past the arch without LOOKING.
But I saw the cobbles under the empty half of the SEAT.
There was a shadow on them, with shoulders as wide as the ARCH.
And nobody there to cast IT.
My summer was going weirdly WELL.
Mrs Varga started giving me my bread for NOTHING.
Mr Ode fixed my bike and waved me OFF.
My landlady said the rent could WAIT.
I called it LUCK.
The next Saturday, Ilan's stack was taller AGAIN.
And the arch seat was EMPTY.
His cap was on his half. His bun was still in its BAG.
On my half, the shadow was SITTING up.
I searched the cafe tables and around the FOUNTAIN.
His phone was ringing on the stone beside his CAP.
It was ME calling.
He came back at dusk. He wouldn't say where he'd BEEN.
His stack hadn't dropped a single BLOCK.
The third Saturday it rained. The square was nearly EMPTY.
Ilan was in the arch seat, bent almost DOUBLE.
And in my half, something sat up STRAIGHT.
It was built like a person. Rose jumper. Cream TROUSERS.
But its shoulders were as wide as the whole SEAT.
One ordinary head, right in the middle, looking at HIM.
And there wasn't a single block on IT.
I looked away, and it was standing over him, one step CLOSER.
It bent its head down to his, until they nearly TOUCHED.
Then Ilan mumbled into his COLLAR.
He said, "Thanks for his bread, Mrs VARGA."
"Thanks for fixing his bike, Mr ODE."
Every time anyone helped me, Ilan went around after and said THANKS.
For ME.
His whole stack was my bread, my bike, my RENT.
And a block lands on whoever says THANKS.
One favour, one block. It can't sit on two HEADS.
So I walked into the arch and sat in my HALF.
The wide thing was GONE.
Then I stood on the seat and told the whole SQUARE.
"Thanks for the bread, Mrs VARGA." A block lifted off his stack onto MINE.
"Thanks for the bike, Mr ODE." CLICK.
"Thanks for waiting on the RENT." CLICK.
Doors opened around the square, and I kept GOING.
By the end, Ilan could look UP again.
He said his neck hadn't felt this good since JUNE.
Mine was the tallest stack in TOWN.
We sat there until the rain STOPPED.
I'm there every Saturday now. I haven't missed ONE.
Our stacks clunk together under the ARCH.
And I'm paying them back, one at a TIME.
In this town, every favour you owe sits on SOMEBODY'S head. Mine were all on HIS.
Something kept my seat for me all SUMMER.
I'm never saying thanks for THAT one.
""".strip().splitlines()

SPOKEN = {"Mrs": "Missus", "Mr": "Mister", "cafe": "cafe"}


def chunks(text):
    toks = text.split()
    merged = [[w] for w in toks]
    phrases, cur = [], []
    for t in merged:
        cur.append(t)
        if t[-1].rstrip('"')[-1] in ".,?!":
            phrases.append(cur)
            cur = []
    if cur:
        phrases.append(cur)
    SPLIT = {1: [1], 2: [2], 3: [3], 4: [2, 2], 5: [3, 2], 6: [3, 3], 7: [3, 2, 2], 8: [3, 3, 2], 9: [3, 3, 3]}
    out = []
    for ph in phrases:
        n = len(ph)
        if n == 1 and out and len(out[-1]) + 1 <= 3 and ph[0][0].isupper() and ph[0][0] != "I":
            pass
        sizes = SPLIT.get(n, [3] * (n // 3) + ([n % 3] if n % 3 else []))
        k = 0
        for s in sizes:
            out.append([w for t in ph[k:k + s] for w in t])
            k += s
    return out


def spoken(words):
    s = []
    for w in words:
        bare = re.sub(r"[^A-Za-z']", "", w)
        w2 = w
        if bare in SPOKEN:
            w2 = w.replace(bare, SPOKEN[bare])
        elif bare.isupper() and len(bare) > 1 and bare not in ("ME",):
            w2 = w.replace(bare, bare.lower())
            if bare in ("ARCH", "BLOCK", "MINE"):
                pass
        elif bare == "ME":
            w2 = w.replace("ME", "me")
        s.append(w2)
    return " ".join(s)


def display(words):
    return " ".join(w.replace("cafe", "cafe") for w in words)


def lines():
    res = []
    for n, t in enumerate(TEXT, 1):
        ch = [[" ".join(c), spoken(c)] for c in chunks(t)]
        res.append({"id": f"L{n:02d}", "who": "narrator", "chunks": ch})
    return res


if __name__ == "__main__":
    for l in lines():
        print(l["id"], " | ".join(c[0] for c in l["chunks"]))
