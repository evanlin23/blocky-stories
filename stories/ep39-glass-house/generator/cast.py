"""The cast, the clouds and the umbrellas of ep39-glass-house (imported by make_story.py)."""


def person(skin, shirt, pants, hair="cap", hair_c="#2a1d15", pattern="solid", pattern_c=None, shoes="#2c2a2a", **kw):
    d = {"age": "adult", "skin": skin, "shirt": shirt, "pattern": pattern, "pants": pants, "shoes": shoes,
         "sleeves": "long", "hair": hair, "hair_c": hair_c, "hat": "none",
         "face": {"eyes": "round", "brows": True, "ink": "#1c1416"}}
    if pattern_c:
        d["pattern_c"] = pattern_c
    d.update(kw)
    return d


cast = {
    "me": person("#f1c9a0", "#d9a531", "#4a4f2c", "swoop", "#3a2618", "knit", "#b88620", "#3a2a22", width=0.88),
    "mum": person("#e8bd98", "#9fb59a", "#2b3a58", "bun", "#8a5a44", "stripes", "#e6dcc0", "#3a2a22",
                  extras=["glasses", "apron"], extra_c="#232f4a", height=0.95, width=0.88,
                  face={"eyes": "round", "brows": True, "ink": "#1c1416", "bags": True}),
    "pell": person("#d9a984", "#f0eee8", "#4a4a50", "cap", "#8a8a8a", hat="ballcap", hat_c="#6b4a2e",
                   face={"eyes": "round", "brows": True, "ink": "#1c1416", "bags": True}),
    "nb1": person("#c98f6a", "#c96a82", "#3a3a52", "long", "#2a1a14", "solid", None, "#2a2a2a", width=0.9),
    "nb2": person("#f0c8a0", "#5a86a8", "#3a3a3a", "buzz", "#6a5a4a"),
    "nb3": person("#a8745a", "#7a9a5a", "#4a3a2a", "spiky", "#1a1410"),
    "cf1": person("#e6b890", "#e0b02a", "#2a2e3a", "swoop", "#4a2a1a", extras=["coat"], zip_c="#8a2a20"),
    "cf2": person("#b88460", "#3f9a5a", "#2a2e3a", "bun", "#2a1a14", extras=["coat"], zip_c="#1f5058"),
    "cn1": person("#e8c09a", "#6a4a7a", "#2a2a36", "swoop", "#5a3a22"),
    "cn2": person("#c08a64", "#a8643a", "#2a2a36", "long", "#1a1210"),
    "cn3": person("#f0cba4", "#3f6a8a", "#2a2a36", "buzz", "#8a7a5a"),
    "wd1": person("#f0c8a0", "#f4f0e6", "#f4f0e6", "bun", "#5a3a22", face={"eyes": "round", "brows": True, "ink": "#1c1416", "freckles": True, "cheeks": "#f0a090"}),
    "wd2": person("#d8a47c", "#2a3250", "#2a3250", "cap", "#1a1410", extras=["tie"], extra_c="#c8472f",
                  face={"eyes": "round", "brows": True, "ink": "#1c1416", "freckles": True}),
    "gs1": person("#f0c8a0", "#e6c04a", "#4a5a7a", "spiky", "#b0602a", face={"eyes": "round", "brows": True, "ink": "#1c1416", "freckles": True}),
    "gs2": person("#e8b890", "#58a85c", "#3a3a3a", "long", "#7a4a2a", face={"eyes": "round", "brows": True, "ink": "#1c1416", "freckles": True}),
}
cast["pell2"] = dict(cast["pell"])

# every character who wears a cloud; the cloud's size, colour, where rain stops
clouds = {
    "me": {"size": 2.0, "color": "#f6f8fb", "under": "#c3c8d0", "grey": "#454c58", "drops": 90, "spread": 1.1},
    "mum": {"size": 1.3, "color": "#6e7681", "grey": "#4d535c", "drops": 90, "emit": 0.1, "gap": 0.12, "off": (0, -0.1)},
    "pell": {"size": 1.0, "drops": 28, "fall": 2.0},
    "pell2": {"size": 1.0, "drops": 28, "fall": 2.0},
    "nb1": {"size": 0.95}, "nb2": {"size": 1.05}, "nb3": {"size": 0.9, "grey": "#5a6270"},
    "cf1": {"size": 1.0, "drops": 40, "floor": 0.88}, "cf2": {"size": 1.0, "drops": 40, "floor": 0.88},
    "cn1": {"size": 1.0, "drops": 40, "gap": 0.5}, "cn2": {"size": 1.0, "drops": 40, "gap": 0.5},
    "cn3": {"size": 1.0, "drops": 40, "gap": 0.5},
    "wd1": {"size": 1.0}, "wd2": {"size": 1.0}, "gs1": {"size": 0.95}, "gs2": {"size": 1.05},
}
umbrellas = {"cn1": {"mat": "umb1"}, "cn2": {"mat": "umb2"}, "cn3": {"mat": "umb3"}, "me": {"mat": "umb4"}}
