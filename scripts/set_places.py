"""Where a story's set.py puts things, without Blender: for scripts/framing.py's "is the named prop in frame".

    places = SetPlaces(story_dir, story, timeline)   # runs set.py's build() against stand-in bpy and mathutils
    places.at(t)  ->  {object name: (world centre xyz, world half size)}   # after set.py's animate(t), if it has one

The real blocky/kit.py is loaded with a stand-in `bpy` whose objects only keep a name, a parent, a location, a
rotation, a scale, a hidden flag and their mesh's vertices, so kit.box / cyl / sphere / plane / empty / mesh_obj /
light work unchanged. Anything else Blender would do (materials, modifiers, images, lights) is swallowed. A set.py
this can't run raises, and framing.py carries on without props (it says so in its header).
"""

from __future__ import annotations

import contextlib
import importlib.util
import math
import sys
import types
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent


class Any:
    """Swallows everything: any attribute, call, item, number."""

    def __init__(self, *a, **k):
        pass

    def __getattr__(self, k):
        if k.startswith("__") and k.endswith("__"):
            raise AttributeError(k)
        return Any()

    def __call__(self, *a, **k):
        return Any()

    def __getitem__(self, k):
        return Any()

    def __setitem__(self, k, v):
        pass

    def __iter__(self):   # one of anything: `next(n for n in nodes if n.type == "X")` finds it
        return iter((Any(), Any(), Any()))

    def __len__(self):
        return 1

    def __bool__(self):
        return False

    def __float__(self):
        return 0.0

    def __int__(self):
        return 0

    def __index__(self):
        return 0

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def _op(self, *a):
        return Any()

    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __truediv__ = __rtruediv__ = _op
    __neg__ = __matmul__ = __rmatmul__ = __pow__ = __floordiv__ = __mod__ = _op

    def __lt__(self, o):
        return False

    __le__ = __gt__ = __ge__ = __lt__

    def __eq__(self, o):   # matches whatever it's looked up by
        return True

    def __ne__(self, o):
        return False

    def __hash__(self):
        return id(self)

    def __contains__(self, o):
        return False


class Vec:
    """mathutils.Vector, enough of it."""

    def __init__(self, v=(0.0, 0.0, 0.0)):
        object.__setattr__(self, "v", np.array([float(a) for a in v], float))

    def __getattr__(self, k):
        i = "xyzw".find(k)
        if len(k) == 1 and 0 <= i < len(self.v):
            return float(self.v[i])
        if k == "length":
            return float(np.linalg.norm(self.v))
        raise AttributeError(k)

    def __setattr__(self, k, val):
        i = "xyzw".find(k)
        if len(k) == 1 and 0 <= i < len(self.v):
            self.v[i] = float(val)
        else:
            object.__setattr__(self, k, val)

    def __getitem__(self, i):
        r = self.v[i]
        return Vec(r) if isinstance(i, slice) else float(r)

    def __setitem__(self, i, val):
        self.v[i] = val

    def __iter__(self):
        return iter(float(a) for a in self.v)

    def __len__(self):
        return len(self.v)

    def _o(self, o):
        return o.v if isinstance(o, Vec) else np.asarray(o, float) if isinstance(o, (tuple, list)) else o

    def __add__(self, o):
        return Vec(self.v + self._o(o))

    __radd__ = __add__

    def __sub__(self, o):
        return Vec(self.v - self._o(o))

    def __rsub__(self, o):
        return Vec(self._o(o) - self.v)

    def __mul__(self, o):
        return Vec(self.v * self._o(o))

    __rmul__ = __mul__

    def __truediv__(self, o):
        return Vec(self.v / o)

    def __neg__(self):
        return Vec(-self.v)

    def __matmul__(self, o):
        return float(self.v @ self._o(o))

    def dot(self, o):
        return float(self.v @ self._o(o))

    def cross(self, o):
        return Vec(np.cross(self.v, self._o(o)))

    def normalized(self):
        n = np.linalg.norm(self.v)
        return Vec(self.v / n if n > 1e-12 else self.v)

    def normalize(self):
        n = np.linalg.norm(self.v)
        if n > 1e-12:
            self.v /= n

    def copy(self):
        return Vec(self.v)

    def rotate(self, *a):
        pass

    def to_tuple(self, *a):
        return tuple(self)

    def lerp(self, o, u):
        return Vec(self.v + (self._o(o) - self.v) * u)

    def to_track_quat(self, *a):
        return Any()

    def freeze(self):
        return self

    def __repr__(self):
        return f"Vec({list(self.v)})"


def _rot(axis: str, a: float) -> np.ndarray:
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    i, j = {"X": (1, 2), "Y": (2, 0), "Z": (0, 1)}[axis]
    m[i, i], m[i, j], m[j, i], m[j, j] = c, -s, s, c
    return m


def euler(r) -> np.ndarray:
    r = list(r) + [0.0] * (3 - len(list(r)))
    return _rot("Z", r[2]) @ _rot("Y", r[1]) @ _rot("X", r[0])


class Mat:
    """mathutils.Matrix, enough of it."""

    def __init__(self, m=None):
        self.m = np.eye(4) if m is None else np.array(m, float)
        if self.m.shape == (3, 3):
            e = np.eye(4)
            e[:3, :3] = self.m
            self.m = e

    @staticmethod
    def Rotation(a, size=4, axis="Z"):
        if not isinstance(axis, str):
            ax = np.asarray(list(axis), float)
            ax /= np.linalg.norm(ax) + 1e-12
            k = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
            return Mat(np.eye(3) + math.sin(a) * k + (1 - math.cos(a)) * k @ k)
        return Mat(_rot(axis.upper(), a))

    @staticmethod
    def Translation(v):
        m = np.eye(4)
        m[:3, 3] = list(v)[:3]
        return Mat(m)

    @staticmethod
    def Diagonal(v):
        d = list(v) + [1.0] * (4 - len(list(v)))
        return Mat(np.diag(d[:4]))

    @staticmethod
    def Scale(f, size=4, axis=None):
        return Mat(np.diag([f, f, f, 1.0]))

    @staticmethod
    def LocRotScale(loc, rot, scale):
        m = Mat.Translation(loc or (0, 0, 0)).m
        if rot is not None:
            m = m @ (rot.m if isinstance(rot, Mat) else euler(rot))
        if scale is not None:
            m = m @ np.diag(list(scale)[:3] + [1.0])
        return Mat(m)

    def __matmul__(self, o):
        if isinstance(o, Mat):
            return Mat(self.m @ o.m)
        v = list(o)
        return Vec((self.m @ np.array(v[:3] + [1.0]))[:3]) if len(v) == 3 else Vec(self.m @ np.array(v))

    def to_translation(self):
        return Vec(self.m[:3, 3])

    @property
    def translation(self):
        return Vec(self.m[:3, 3])

    def to_euler(self, *a):
        return Vec((0, 0, math.atan2(self.m[1, 0], self.m[0, 0])))

    def to_3x3(self):
        return Mat(self.m[:3, :3])

    def to_4x4(self):
        return Mat(self.m)

    def inverted(self, *a):
        return Mat(np.linalg.inv(self.m))

    def copy(self):
        return Mat(self.m)

    def decompose(self):
        return self.to_translation(), Any(), Vec(np.linalg.norm(self.m[:3, :3], axis=0))


class Eul(Vec):
    def __init__(self, v=(0.0, 0.0, 0.0), order="XYZ"):
        super().__init__(v)

    def rotate_axis(self, axis, a):
        self.v["XYZ".index(axis.upper())] += a

    def to_matrix(self):
        return Mat(euler(self.v)[:3, :3])


class Mesh(Any):
    def __init__(self, name=""):
        object.__setattr__(self, "verts", np.zeros((0, 3)))

    def from_pydata(self, verts, edges, faces):
        object.__setattr__(self, "verts", np.array([list(v)[:3] for v in verts], float).reshape(-1, 3))


class Obj:
    """A bpy object: a name, a parent, location / rotation_euler / scale, hide flags and its mesh's vertices."""

    def __init__(self, name, data=None):
        d = self.__dict__
        d.update(name=name, data=data if data is not None else Any(), parent=None, children=[],
                 location=Vec(), rotation_euler=Eul(), scale=Vec((1, 1, 1)), hide_render=False, hide_viewport=False,
                 _extra={})
        d["type"] = "MESH" if isinstance(data, Mesh) else "EMPTY"

    def __setattr__(self, k, v):
        if k in ("location", "scale"):
            self.__dict__[k] = Vec(v)
        elif k == "rotation_euler":
            self.__dict__[k] = Eul(v)
        elif k == "parent":
            old = self.__dict__.get("parent")
            if old is not None and self in old.children:
                old.children.remove(self)
            self.__dict__["parent"] = v if isinstance(v, Obj) else None
            if isinstance(v, Obj):
                v.children.append(self)
        elif k == "matrix_world":
            pass
        else:
            self.__dict__[k] = v

    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        return self.__dict__["_extra"].setdefault(k, Any())

    def local(self) -> np.ndarray:
        m = np.eye(4)
        m[:3, 3] = self.location.v[:3]
        return m @ euler(self.rotation_euler.v) @ np.diag(list(self.scale.v[:3]) + [1.0])

    def world(self) -> np.ndarray:
        m, o, seen = self.local(), self.parent, 0
        while o is not None and seen < 64:
            m = o.local() @ m
            o, seen = o.parent, seen + 1
        return m

    @property
    def matrix_world(self):
        return Mat(self.world())

    @property
    def children_recursive(self):
        out = []
        for c in self.children:
            out += [c] + c.children_recursive
        return out

    def hidden(self) -> bool:
        o, seen = self, 0
        while o is not None and seen < 64:
            if o.hide_render is True:
                return True
            o, seen = o.parent, seen + 1
        return False

    def __getitem__(self, k):
        return self.__dict__["_extra"].setdefault(("item", k), Any())

    def __setitem__(self, k, v):
        self.__dict__["_extra"][("item", k)] = v

    def __contains__(self, k):
        return ("item", k) in self.__dict__["_extra"]

    def get(self, k, default=None):
        return self.__dict__["_extra"].get(("item", k), default)

    def under(self, other) -> bool:
        o, seen = self, 0
        while o is not None and seen < 64:
            if o is other:
                return True
            o, seen = o.parent, seen + 1
        return False

    def visible_get(self, *a):
        return not self.hidden()

    def select_set(self, *a):
        pass

    def keyframe_insert(self, *a, **k):
        pass

    def copy(self):
        return Obj(self.name, self.data)

    def __repr__(self):
        return f"Obj({self.name})"


class Objects:
    def __init__(self):
        self.d: dict[str, Obj] = {}

    def new(self, name, data=None):
        base, k = name, 1
        while name in self.d:
            name, k = f"{base}.{k:03d}", k + 1
        ob = Obj(name, data)
        self.d[name] = ob
        return ob

    def __getitem__(self, k):   # something set.py didn't make here (a rig's part): a stand-in, not a prop
        return self.d[k] if k in self.d else Obj(k)

    def get(self, k, default=None):
        return self.d.get(k, default)

    def __contains__(self, k):
        return k in self.d

    def __iter__(self):
        return iter(list(self.d.values()))

    def __len__(self):
        return len(self.d)

    def remove(self, ob, **k):
        self.d.pop(getattr(ob, "name", None), None)

    def keys(self):
        return self.d.keys()

    def values(self):
        return self.d.values()

    def items(self):
        return self.d.items()


def stand_ins() -> tuple[types.ModuleType, types.ModuleType, Objects]:
    objs = Objects()
    bpy = types.ModuleType("bpy")
    data = Any()
    object.__setattr__(data, "objects", objs)
    meshes = Any()
    object.__setattr__(meshes, "new", lambda name="", *a, **k: Mesh(name))
    object.__setattr__(data, "meshes", meshes)
    bpy.data = data
    bpy.context = Any()
    bpy.ops = Any()
    bpy.types = Types("bpy.types")
    bpy.app = Any()
    bpy.props = Any()
    mu = types.ModuleType("mathutils")
    mu.Vector, mu.Matrix, mu.Euler, mu.Quaternion, mu.Color = Vec, Mat, Eul, Any, Any
    bvh = types.ModuleType("mathutils.bvhtree")
    bvh.BVHTree = Any
    mu.bvhtree = bvh
    noise = types.ModuleType("mathutils.noise")
    noise.noise = lambda *a, **k: 0.0
    mu.noise = noise
    return bpy, mu, objs


GEOMETRY = {"empty", "mesh_obj", "box", "cyl", "sphere", "plane", "box_verts", "link", "srgb", "col", "ss", "lerp",
            "bump", "spring", "noise1", "hash01", "_dip", "flicker_gain", "aim"}


def _forgiving(f):
    def g(*a, **k):
        try:
            return f(*a, **k)
        except Exception:
            return Any()
    g.__name__ = f.__name__
    return g


class AnyModule(types.ModuleType):
    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        return Any()


class Types(types.ModuleType):
    """bpy.types: every name is a class nothing is an instance of."""
    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        return type(k, (), {})


class Missing(dict):
    def __missing__(self, k):
        return Any()


class SetPlaces:
    def __init__(self, story_dir: Path, story: dict, tl: dict):
        bpy, mu, objs = stand_ins()
        self.objs = objs
        bx = types.ModuleType("bpy_extras")
        bxo = types.ModuleType("bpy_extras.object_utils")
        bxo.world_to_camera_view = lambda *a: Vec((0.5, 0.5, -1))
        bx.object_utils = bxo
        self.mods = {"bpy": bpy, "mathutils": mu, "mathutils.bvhtree": mu.bvhtree, "mathutils.noise": mu.noise,
                     "bpy_extras": bx, "bpy_extras.object_utils": bxo, "bmesh": AnyModule("bmesh")}
        self.story_dir, self.story, self.tl = story_dir, story, tl
        with self._stubbed(fresh_layout=True):
            spec = importlib.util.spec_from_file_location("_framing_kit", ROOT / "blocky" / "kit.py")
            kit = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(kit)
            for k, f in list(vars(kit).items()):   # materials, lights, the world: swallowed if they trip
                if callable(f) and isinstance(f, types.FunctionType) and k not in GEOMETRY:
                    setattr(kit, k, _forgiving(f))
            kit.prop = self._prop(kit)
            for k in ("MATS", "LIGHTS", "OBJ"):
                if isinstance(getattr(kit, k, None), dict):
                    setattr(kit, k, Missing(getattr(kit, k)))
            self.cam = objs.new("cam")   # the camera: a set's tag (the HUD) rides on it, so it's never a prop
            self.cam.data = Any()
            kit.OBJ["cam"] = self.cam
            self.kit = kit
            self.mods["blocky.kit"] = kit
            sys.modules["blocky.kit"] = kit
            spec = importlib.util.spec_from_file_location(f"_framing_set_{story_dir.name}", story_dir / "set.py")
            sm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(sm)
            self.setmod = sm
            self.ctx = sm.build(kit, story, tl) or {}
        self.animate_ok = hasattr(self.setmod, "animate")
        self.error = None

    @contextlib.contextmanager
    def _stubbed(self, fresh_layout=False):
        """The stand-in modules in sys.modules (and the story's folder on the path) for the length of the block."""
        names = list(self.mods) + ["blocky.kit", "layout"]
        saved = {k: sys.modules.get(k) for k in names}
        pkg = sys.modules.get("blocky")
        had_kit = pkg is not None and "kit" in vars(pkg)
        old_kit = vars(pkg).get("kit") if had_kit else None
        path_saved = list(sys.path)
        sys.modules.update(self.mods)
        if fresh_layout:
            sys.modules.pop("layout", None)
        elif getattr(self, "layout", None) is not None:
            sys.modules["layout"] = self.layout
        if pkg is not None and "blocky.kit" in self.mods:
            pkg.kit = self.mods["blocky.kit"]
        sys.path.insert(0, str(self.story_dir))
        try:
            yield
        finally:
            self.layout = sys.modules.get("layout")
            sys.path[:] = path_saved
            for k, v in saved.items():
                if v is None:
                    sys.modules.pop(k, None)
                else:
                    sys.modules[k] = v
            if pkg is not None:
                if had_kit:
                    pkg.kit = old_kit
                elif "kit" in vars(pkg):
                    del pkg.kit

    def _prop(self, kit):
        def prop(name, loc=(0, 0, 0), rot=0.0, scale=1.0, height=None, fit=None, tint=None, parent=None):
            rec = kit.props().get(name) or {"size_m": [1.0, 1.0, 1.0]}
            size = rec["size_m"]
            k = height / max(size[2], 1e-6) if height else fit / max(max(size), 1e-6) if fit else scale
            me = Mesh(name)
            sx, sy, sz = size
            me.from_pydata([(a * sx / 2, b * sy / 2, c * sz) for a in (-1, 1) for b in (-1, 1) for c in (0, 1)], [], [])
            ob = self.objs.new(name, me)
            ob.scale = (k, k, k)
            ob.location = loc
            ob.rotation_euler = (0.0, 0.0, math.radians(rot))
            if isinstance(parent, Obj):
                ob.parent = parent
            return ob
        return prop

    def hud(self, lens: float) -> list[tuple[float, float, float, float]]:
        """The boxes (x0, y0, x1, y1, in -1..1 across the frame) of what set.py hangs on the camera (a rule tag),
        as last placed by animate. The camera stand-in never moves, so their places are camera-local: x right,
        y up, -z ahead, the frame's half height at depth d is d * 12 / lens (Blender: 24 mm sensor, vertical)."""
        out = []
        for ob in self.objs:
            if ob.type != "MESH" or not len(ob.data.verts) or ob.hidden() or not ob.under(self.cam) or ob is self.cam:
                continue
            w = ob.world()
            p = (w @ np.c_[ob.data.verts, np.ones(len(ob.data.verts))].T)[:3].T
            p = p[p[:, 2] < -1e-4]
            if not len(p):
                continue
            hh = -p[:, 2] * 12.0 / lens
            xs, ys = p[:, 0] / (hh * 1080 / 1920), p[:, 1] / hh
            out.append((float(xs.min()), float(ys.min()), float(xs.max()), float(ys.max())))
        return out

    def at(self, t: float) -> dict:
        """Every visible mesh object at time t: name -> (world centre, world half size)."""
        if self.animate_ok:
            with self._stubbed():
                try:
                    self.setmod.animate(self.kit, self.story, self.tl, t, self.ctx)
                except Exception as e:   # an animate this can't run: the places stay as build() left them
                    self.animate_ok, self.error = False, f"animate: {type(e).__name__}: {e}"
        out = {}
        for ob in self.objs:
            if ob.type != "MESH" or not len(ob.data.verts) or ob.hidden() or ob.under(self.cam):
                continue
            w = ob.world()
            p = (w @ np.c_[ob.data.verts, np.ones(len(ob.data.verts))].T)[:3].T
            lo, hi = p.min(0), p.max(0)
            out[ob.name] = ((lo + hi) / 2, (hi - lo) / 2)
        return out
