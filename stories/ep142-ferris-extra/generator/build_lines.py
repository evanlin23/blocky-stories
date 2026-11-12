"""Writes lines.json from the script's caption chunks (caption text, spoken text). Run once; edit lines.json after."""
import json
from pathlib import Path

L = [
 ("L01", [("Four of us", "four of us"), ("got on", "got on"), ("the Ferris WHEEL.", "the ferris wheel.")]),
 ("L02", [("FIVE", "five"), ("got off.", "got off.")]),
 ("P02", 0.3),
 ("L03", [("Find the", "find the"), ("EXTRA one.", "extra one.")]),
 ("L04", [("A.", "ay,")]),
 ("P04a", 0.15),
 ("L04b", [("B.", "bee,")]),
 ("P04b", 0.15),
 ("L04c", [("C.", "see,")]),
 ("P04c", 0.15),
 ("L04d", [("D.", "dee,")]),
 ("P04d", 0.15),
 ("L04e", [("E.", "ee.")]),
 ("L05", [("I'm B.", "i'm bee."), ("Three are my COUSINS.", "three are my cousins.")]),
 ("L06", [("We bought cones", "we bought cones"), ("at four o'CLOCK.", "at four o'clock.")]),
 ("L07", [("In this heat,", "in this heat,"), ("they melt", "they melt"), ("in two MINUTES.", "in two minutes.")]),
 ("L08", [("You've got", "you've got"), ("one TURN.", "one turn.")]),
 ("L09", [("Which ONE?", "which one?")]),
 ("P01", 3.5),
 ("L10", [("It's D.", "it's dee.")]),
 ("L11", [("Four cones", "four cones"), ("are dripping", "are dripping"), ("down four WRISTS.", "down four wrists.")]),
 ("L12", [("D's is still", "dee's is still"), ("FROSTY.", "frosty.")]),
 ("L13", [("Every shadow", "every shadow"), ("points AWAY", "points away"), ("from the sun.", "from the sun.")]),
 ("L14", [("D's points", "dee's points"), ("right AT it.", "right at it.")]),
 ("L15", [("D got on", "dee got on"), ("at the TOP.", "at the top.")]),
 ("L16", [("Nobody gets on", "nobody gets on"), ("at the top.", "at the top.")]),
 ("L17", [("The man at the gate", "the man at the gate"), ("tips his HAT", "tips his hat"), ("to D.", "to dee.")]),
 ("L18", [("Like he does", "like he does"), ("every DAY.", "every day.")]),
 ("L19", [("D walks", "dee walks"), ("back through", "back through"), ("the GATE.", "the gate.")]),
 ("L20", [("And gets on", "and gets on"), ("ALONE.", "alone.")]),
 ("L21", [("At the top,", "at the top,"), ("D waits", "dee waits")]),
 ("L22", [("for the", "for the"), ("next FOUR.", "next four.")]),
]
out = []
for i, ch in L:
    if isinstance(ch, float):
        out.append({"id": i, "pause": ch, "chunks": []})
    elif i == "P01":
        out.append({"id": i, "pause": 3.5, "chunks": []})
    else:
        out.append({"id": i, "who": "narrator", "chunks": [[a, b] for a, b in ch]})
# P01 is a float 3.5 too
Path(__file__).with_name("lines.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
