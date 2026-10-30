from collections.abc import Iterator
from dataclasses import dataclass

from dazl.damlast import daml_lf_1 as lf

LF_MODULE = lf.__name__
OPAQUE = (int, str, lf.Type, lf.Location, lf.Kind, lf.DottedName, lf.ModuleRef, lf._Name)
SKIP = frozenset({"_lazy_lock", "_expr_fn", "location"})


@dataclass(frozen=True)
class Visit:
    node: lf.Expr | lf.Update
    loc: lf.Location | None

    @property
    def kind(self) -> str:
        return self.node._Sum_name

    @property
    def value(self) -> object:
        return self.node._Sum_value


def children(obj: object) -> list[object]:
    names: list[str] = []
    for cls in type(obj).__mro__:
        slots = getattr(cls, "__slots__", ())
        names.extend([slots] if isinstance(slots, str) else slots)
    names.extend(getattr(obj, "__dict__", {}))
    return [getattr(obj, n, None) for n in dict.fromkeys(names) if n not in SKIP]


def walk(root: object, loc: lf.Location | None = None) -> Iterator[Visit]:
    stack: list[tuple[object, lf.Location | None]] = [(root, loc)]
    while stack:
        obj, loc = stack.pop()
        if isinstance(obj, (lf.Expr, lf.Update)):
            loc = getattr(obj, "location", None) or loc
            yield Visit(obj, loc)
            stack.append((obj._Sum_value, loc))
            continue
        if isinstance(obj, (tuple, list)):
            items = list(obj)
        elif type(obj).__module__ == LF_MODULE and not isinstance(obj, OPAQUE):
            items = children(obj)
        else:
            continue
        stack.extend((item, loc) for item in reversed(items))


def find(root: object, kind: str) -> Iterator[Visit]:
    return (v for v in walk(root) if v.kind == kind)
