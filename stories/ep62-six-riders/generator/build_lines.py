"""Writes lines.json from the script's caption chunks (caption text, spoken text). Run once; edit lines.json after."""
import json
from pathlib import Path

L = [
 ("L01", [("Four people", "four people"), ("got in", "got in"), ("the ELEVATOR.", "the elevator."), ("The mirror", "the mirror"), ("shows FIVE.", "shows five.")]),
 ("L02", [("Find the", "find the"), ("EXTRA one.", "extra one.")]),
 ("L03", [("We're all", "we're all"), ("facing the", "facing the"), ("MIRROR doors.", "mirror doors.")]),
 ("L04", [("A.", "ay,"), ("B.", "bee,"), ("C.", "see,"), ("D.", "dee,")]),
 ("L05", [("I'm D.", "i'm dee.")]),
 ("L06", [("Match every", "match every"), ("FACE", "face"), ("to a BACK.", "to a back.")]),
 ("L07", [("You've got", "you've got"), ("three FLOORS.", "three floors.")]),
 ("P01", None),
 ("L08", [("There are", "there are"), ("TWO of C.", "two of see.")]),
 ("L09", [("C is my", "see is my"), ("big BROTHER.", "big brother.")]),
 ("L10", [("His BAG'S", "his bag's"), ("on his", "on his"), ("RIGHT shoulder.", "right shoulder.")]),
 ("L11", [("His reflection", "his reflection"), ("wears it", "wears it"), ("on its LEFT.", "on its left."), ("The other one,", "the other one,"), ("on its RIGHT.", "on its right.")]),
 ("L12", [("Mirrors", "mirrors"), ("FLIP you.", "flip you."), ("That one", "that one"), ("DIDN'T.", "didn't.")]),
 ("L13", [("Something", "something"), ("in the GLASS", "in the glass"), ("is PRACTICING", "is practicing"), ("being HIM.", "being him.")]),
 ("P02", None),
 ("L14", [("The doors", "the doors"), ("OPEN.", "open."), ("Nobody", "nobody"), ("gets ON.", "gets on.")]),
 ("L15", [("The doors", "the doors"), ("CLOSE.", "close.")]),
 ("L16", [("The C", "the see"), ("in front", "in front"), ("of me", "of me"), ("has his bag", "has his bag"), ("on the", "on the"), ("OTHER shoulder.", "other shoulder.")]),
 ("L17", [("His letter's", "his letter's"), ("BACKWARDS.", "backwards.")]),
 ("L18", [("My REAL brother", "my real brother"), ("is in", "is in"), ("the GLASS.", "the glass.")]),
 ("L19", [("Now the", "now the"), ("EXTRA one's", "extra one's"), ("out HERE.", "out here.")]),
]
out = []
for i, ch in L:
    if ch is None:
        out.append({"id": i, "pause": 3.0 if i == "P01" else 0.6, "chunks": []})
    else:
        out.append({"id": i, "who": "narrator", "chunks": [[a, b] for a, b in ch]})
Path(__file__).with_name("lines.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
