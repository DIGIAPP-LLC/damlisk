from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

from dazl.damlast import daml_lf_1 as lf

Term = lf.Expr | lf.Update
T = TypeVar("T")

LEAVES = (int, str, lf.Type, lf.Location, lf.Kind, lf.DottedName, lf.ModuleRef, lf._Name)
HIDDEN = frozenset({"_lazy_lock", "_expr_fn", "location"})


@dataclass(frozen=True)
class Found(Generic[T]):
    node: T
    loc: lf.Location | None


def is_lf_record(obj: object) -> bool:
    return type(obj).__module__ == lf.__name__ and not isinstance(obj, LEAVES)


def record_fields(obj: object) -> list[object]:
    names: list[str] = []
    classes = type(obj).__mro__
    for cls in classes:
        slots = getattr(cls, "__slots__", ())
        names.extend([slots] if isinstance(slots, str) else slots)
    names.extend(getattr(obj, "__dict__", {}))
    unique = dict.fromkeys(name for name in names if name not in HIDDEN)
    return [getattr(obj, name, None) for name in unique]


def collect_terms(obj: object, found: list[Term]) -> None:
    if isinstance(obj, (lf.Expr, lf.Update)):
        found.append(obj)
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            collect_terms(item, found)
    elif is_lf_record(obj):
        values = record_fields(obj)
        for value in values:
            collect_terms(value, found)


def child_terms(term: Term) -> list[Term]:
    found: list[Term] = []
    collect_terms(term._Sum_value, found)
    return found


def all_terms(root: Term, loc: lf.Location | None = None) -> Iterator[Found[Term]]:
    loc = getattr(root, "location", None) or loc
    yield Found(root, loc)
    children = child_terms(root)
    for child in children:
        yield from all_terms(child, loc)


def find_all(root: Term, kind: type[T], loc: lf.Location | None = None) -> list[Found[T]]:
    matches: list[Found[T]] = []
    terms = all_terms(root, loc)
    for term in terms:
        content = term.node._Sum_value
        if isinstance(content, kind):
            matches.append(Found(content, term.loc))
    return matches
