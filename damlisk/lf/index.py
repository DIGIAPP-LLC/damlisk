import re
from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.util import module_local_name, package_ref

from damlisk.lf.dar import Dar, LfPackage
from damlisk.lf.lf2 import DefException, Implements
from damlisk.lf.walk import walk

TMPL_ATTRS = ("precond", "signatories", "observers")
KEY_ATTRS = ("complex_key", "maintainers")
CH_ATTRS = ("controllers", "observers", "authorizers", "update")
NO_RANGE = (0, 0, 0, 0)


@dataclass(frozen=True)
class Body:
    owner: str
    expr: lf.Expr
    loc: lf.Location | None


def known(loc: lf.Location | None) -> lf.Location | None:
    if loc is None:
        return None
    rng = loc.range
    return None if (rng.start_line, rng.start_col, rng.end_line, rng.end_col) == NO_RANGE else loc


def decl_re(keyword: str, name: str) -> re.Pattern[str]:
    return re.compile(rf"^\s*(?:\w+\s+)?({keyword}\s+{re.escape(name)})\b")


def value_re(name: str) -> re.Pattern[str]:
    return re.compile(rf"^({re.escape(name)})\s*:")


def fields(
    owner: str, obj: object, names: Iterable[str], loc: lf.Location | None
) -> Iterator[Body]:
    for name in names:
        expr = getattr(obj, name)
        if expr is not None:
            yield Body(f"{owner}.{name}", expr, loc)


@dataclass(frozen=True)
class Scope:
    pkg: LfPackage
    module: lf.Module
    lines: tuple[str, ...]

    @property
    def ref(self) -> lf.ModuleRef:
        return lf.ModuleRef(lf.PackageRef(self.pkg.pkg_id), self.module.name)

    def qual(self, *parts: str) -> str:
        return f"{self.module.name}:{'.'.join(parts)}"

    def locate(self, pattern: re.Pattern[str], first: int = 0) -> lf.Location | None:
        for no in range(first, len(self.lines)):
            match = pattern.match(self.lines[no])
            if match:
                rng = lf.Location.Range(no, match.start(1), no, len(self.lines[no]))
                return lf.Location(self.ref, rng)
        return None

    def decls(self) -> Iterator[Body]:
        for tmpl in self.module.templates:
            owner = self.qual(*tmpl.tycon.segments)
            head = known(tmpl.location) or self.locate(decl_re("template", tmpl.tycon.segments[-1]))
            yield from fields(owner, tmpl, TMPL_ATTRS, head)
            if tmpl.key is not None:
                yield from fields(owner, tmpl.key, KEY_ATTRS, head)
            yield from self.choices(owner, tmpl.choices, head)
        for iface in self.module.interfaces:
            head = self.locate(decl_re("interface", iface.name.segments[-1]))
            yield from self.choices(self.qual(*iface.name.segments), iface.choices, head)

    def choices(
        self, owner: str, choices: Iterable[lf.TemplateChoice], head: lf.Location | None
    ) -> Iterator[Body]:
        first = head.range.start_line if head else 0
        for ch in choices:
            loc = known(ch.location) or self.locate(decl_re("choice", ch.name), first) or head
            yield from fields(f"{owner}.{ch.name}", ch, CH_ATTRS, loc)

    def values(self, alias: dict[lf.ValName, Body]) -> Iterator[Body]:
        for dv in self.module.values:
            name = dv.name_with_type.name
            parent = alias.get(lf.ValName(self.ref, name))
            if parent is not None:
                yield Body(parent.owner, dv.expr, parent.loc)
            else:
                loc = known(dv.location) or self.locate(value_re(name[-1]))
                yield Body(self.qual(*name), dv.expr, loc)


class PackageIndex:
    def __init__(self, dar: Dar) -> None:
        self.dar = dar
        self.packages = {p.pkg_id: p for p in dar.packages}
        self.values: dict[lf.ValName, lf.DefValue] = {}
        self.templates: dict[lf.TypeConName, lf.DefTemplate] = {}
        self.ifaces: dict[lf.TypeConName, lf.DefInterface] = {}
        self.impls: dict[lf.TypeConName, list[Implements]] = {}
        self.exceptions: dict[lf.TypeConName, DefException] = {}
        for pkg in dar.packages:
            for scope in self.scopes(pkg):
                ref, mod = scope.ref, scope.module
                self.values.update((lf.ValName(ref, v.name_with_type.name), v) for v in mod.values)
                self.templates.update(
                    (lf.TypeConName(ref, t.tycon.segments), t) for t in mod.templates
                )
                self.ifaces.update(
                    (lf.TypeConName(ref, i.name.segments), i) for i in mod.interfaces
                )
            for impl in pkg.extras.implements:
                self.impls.setdefault(impl.template, []).append(impl)
            self.exceptions.update((e.name, e) for e in pkg.extras.exceptions)

    def scopes(self, pkg: LfPackage) -> Iterator[Scope]:
        for module in pkg.modules:
            text = self.dar.sources.get(str(module.name), "") if pkg is self.dar.main else ""
            yield Scope(pkg, module, tuple(text.splitlines()))

    def bodies(self, pkg: LfPackage | None = None) -> Iterator[Body]:
        pkg = pkg or self.dar.main
        scopes = list(self.scopes(pkg))
        decls = [body for scope in scopes for body in scope.decls()]
        alias = aliases(decls, pkg, self.values)
        yield from decls
        for scope in scopes:
            yield from scope.values(alias)
        for impl in pkg.extras.implements:
            owner = f"{impl.template}@{impl.interface}"
            yield Body(f"{owner}.view", impl.view, impl.location)
            yield from (Body(f"{owner}.{n}", e, impl.location) for n, e in impl.methods.items())
        for exc in pkg.extras.exceptions:
            yield Body(f"{exc.name}.message", exc.message, exc.location)


def aliases(
    decls: Iterable[Body], pkg: LfPackage, values: dict[lf.ValName, lf.DefValue]
) -> dict[lf.ValName, Body]:
    out: dict[lf.ValName, Body] = {}
    todo = deque(decls)
    while todo:
        body = todo.popleft()
        for visit in walk(body.expr, body.loc):
            name = visit.value
            if not isinstance(name, lf.ValName) or name in out or package_ref(name) != pkg.pkg_id:
                continue
            if module_local_name(name).startswith("$") and name in values:
                out[name] = body
                todo.append(Body(body.owner, values[name].expr, body.loc))
    return out
