"""The v3 look (docs/research/style-v3/): faces, the hair library and the checks. No Blender."""

from blocky import faces_v3 as F, hair3


def test_every_expression_draws_and_differs():
    seen = set()
    for e in F.EXPRESSIONS3:
        im = F.face3_image({}, "#e9b48a", e)
        assert im.size == (F.TEX3_W, F.TEX3_H) and im.mode == "RGBA"
        a = im.getchannel("A")
        assert a.getextrema() == (0, 255)                      # ink on a clear ground: the skin shows through
        seen.add(im.resize((64, 54)).tobytes())
    assert len(F.EXPRESSIONS3) >= 12 and len(seen) == len(F.EXPRESSIONS3)


def test_v2_names_map_to_v3_faces():
    from blocky import faces
    for e in faces.EXPRESSIONS:
        assert F.resolve(e) in F.FACES3
    assert F.resolve("not-a-face") == "neutral"


def test_flat_faces_no_shading():
    # every opaque pixel is one of a few flat colours (ink, white, the mouth, the accents), never a gradient
    im = F.face3_image({}, "#e9b48a", "heartbroken")
    px = [p[:3] for p in im.convert("RGBA").getdata() if p[3] == 255]
    common = {c for c, n in __import__("collections").Counter(px).most_common(12)}
    share = sum(1 for p in px if p in common) / len(px)
    assert share > 0.97


def test_nothing_above_the_hairline():
    # a fringe covers the top of the face: no expression draws there, not even brows flying up
    for e in F.EXPRESSIONS3:
        im = F.face3_image({}, "#e9b48a", e)
        top = im.crop((int(F.TEX3_W * 0.15), 0, int(F.TEX3_W * 0.85), int(F.TEX3_H * F.HAIRLINE) - 2))
        a = top.getchannel("A")
        assert a.getextrema()[1] < 128, e


def test_talking_opens_the_mouth_and_pop_and_blink_change_it():
    shut = F.face3_image({}, "#e9b48a", "neutral")
    open_ = F.face3_image({}, "#e9b48a", "neutral", open_=1.0)
    assert shut.tobytes() != open_.tobytes()
    assert F.face3_image({}, "#e9b48a", "shocked", pop=1.0).tobytes() != F.face3_image({}, "#e9b48a", "shocked").tobytes()
    assert F.face3_image({}, "#e9b48a", "neutral", blink=1.0).tobytes() != shut.tobytes()


def test_keys_are_quantised_and_style_aware():
    k1 = F.face3_key({}, "#e9b48a", "neutral", 0.31, (0.1, 0), 0.0)
    k2 = F.face3_key({}, "#e9b48a", "neutral", 0.33, (0.12, 0), 0.0)
    assert k1 == k2 and k1.startswith(f"v3.{F.FACE3_VERSION}-")
    assert F.face3_key({"mustache": "#d8622a"}, "#e9b48a", "neutral", 0, (0, 0), 0) != k1
    assert F.face3_key({}, "#e9b48a", "smile", 0, (0, 0), 0) == F.face3_key({}, "#e9b48a", "neutral", 0, (0, 0), 0)


def test_pop_snaps_then_settles():
    assert F.pop_at(-0.1) == 0.0 and F.pop_at(0.0) == 0.0
    assert F.pop_at(F.POP_IN) == 1.0
    assert 0 < F.pop_at(F.POP_IN + 0.1) < 1
    assert F.pop_at(F.POP_IN + F.POP_OUT + 0.01) == 0.0


def test_hair_library():
    assert len([s for s in hair3.STYLES if s != "bald"]) >= 15
    sil = set()
    for st in hair3.STYLES:
        ps = hair3.parts(st)
        for part, size, loc, rot, bev, mat in ps:
            assert all(v > 0 for v in size) and mat in ("hair", "hair2", "skin")
            assert loc[1] > hair3.FRONT - 0.6           # nothing hangs out in front of the face
        names = [p[0] for p in ps]
        assert len(names) == len(set(names)), st        # unique part names: they become object names
        # a rough silhouette signature: how high, wide and deep the hair reaches
        if ps:
            top = max(l[2] + s[2] / 2 for _, s, l, *_ in ps)
            wide = max(abs(l[0]) + s[0] / 2 for _, s, l, *_ in ps)
            low = min(l[2] - s[2] / 2 for _, s, l, *_ in ps)
            sil.add((round(top, 1), round(wide, 1), round(low, 1), len(ps)))
    assert len(sil) == len(hair3.STYLES) - 1            # every style (but bald) has its own silhouette


def test_fringe_stays_above_the_eyes():
    eye_top = hair3.TOP - (F.EYE_Y - F.EYE_RY * 1.3) * hair3.H
    for st in hair3.STYLES:
        for part, size, loc, rot, bev, mat in hair3.parts(st):
            if loc[1] - size[1] / 2 < hair3.FRONT + 0.05 and abs(loc[0]) < hair3.W * 0.35 and rot == (0, 0, 0):
                assert loc[2] - size[2] / 2 > eye_top - 0.05, (st, part)


def test_features_and_unknowns():
    import pytest
    assert {"mustache", "glasses", "beard"} <= set(hair3.FEATURES)
    assert len(hair3.parts("buzz", ["mustache"])) > len(hair3.parts("buzz"))
    with pytest.raises(ValueError):
        hair3.parts("afro-from-somewhere")
    with pytest.raises(ValueError):
        hair3.parts("buzz", ["cape"])


def test_check_original3():
    assert F.check_original3({}) == []
    assert F.check_original3({"brows": False, "eye_scale": 0.4})
