# Copyright 2026 DIGIAPP LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
from collections import deque
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.util import module_local_name, package_ref

from damlisk.lf.builtins import type_owner
from damlisk.lf.dar import Dar, LfPackage
from damlisk.lf.lf2 import DefException, Implements
from damlisk.lf.tree import find_all

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
class ChoiceDecl:
    owner: str
    choice: lf.TemplateChoice
    param: str
    iface: bool
    loc: lf.Location | None

    @property
    def parent(self) -> str:
        """Return the owner (`Module:Template`) of the template or interface of the choice."""
        return self.owner.rsplit(".", 1)[0]

    def bodies(self) -> Iterator[Body]:
        return fields(self.owner, self.choice, CH_ATTRS, self.loc)


@dataclass(frozen=True)
class TemplateDecl:
    owner: str
    template: lf.DefTemplate
    fields: tuple[lf.FieldWithType, ...]
    loc: lf.Location | None


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

    def template_head(self, tmpl: lf.DefTemplate) -> lf.Location | None:
        return known(tmpl.location) or self.locate(decl_re("template", tmpl.tycon.segments[-1]))

    def decls(self) -> Iterator[Body]:
        for tmpl in self.module.templates:
            owner = self.qual(*tmpl.tycon.segments)
            head = self.template_head(tmpl)
            yield from fields(owner, tmpl, TMPL_ATTRS, head)
            if tmpl.key is not None:
                yield from fields(owner, tmpl.key, KEY_ATTRS, head)
            choices = self.choices_of(tmpl, head)
            for decl in choices:
                yield from decl.bodies()
        for iface in self.module.interfaces:
            choices = self.choices_of(iface, self.iface_head(iface))
            for decl in choices:
                yield from decl.bodies()

    def iface_head(self, iface: lf.DefInterface) -> lf.Location | None:
        return self.locate(decl_re("interface", iface.name.segments[-1]))

    def record_fields(self, tmpl: lf.DefTemplate) -> tuple[lf.FieldWithType, ...]:
        for data in self.module.data_types:
            same = tuple(data.name.segments) == tuple(tmpl.tycon.segments)
            if same and data.record is not None:
                return tuple(data.record.fields)
        return ()

    def template_decls(self) -> Iterator[TemplateDecl]:
        for tmpl in self.module.templates:
            owner = self.qual(*tmpl.tycon.segments)
            fields = self.record_fields(tmpl)
            yield TemplateDecl(owner, tmpl, fields, self.template_head(tmpl))

    def choices(self) -> Iterator[ChoiceDecl]:
        for tmpl in self.module.templates:
            yield from self.choices_of(tmpl, self.template_head(tmpl))
        for iface in self.module.interfaces:
            yield from self.choices_of(iface, self.iface_head(iface))

    def choices_of(
        self, decl: lf.DefTemplate | lf.DefInterface, head: lf.Location | None
    ) -> Iterator[ChoiceDecl]:
        if isinstance(decl, lf.DefInterface):
            owner, is_iface = self.qual(*decl.name.segments), True
        else:
            owner, is_iface = self.qual(*decl.tycon.segments), False
        first = head.range.start_line if head else 0
        for ch in decl.choices:
            loc = known(ch.location) or self.locate(decl_re("choice", ch.name), first) or head
            yield ChoiceDecl(f"{owner}.{ch.name}", ch, decl.param, is_iface, loc)

    def own_body(self, dv: lf.DefValue) -> Body:
        """Return value `dv` as a body under its own name and source line."""
        name = dv.name_with_type.name
        loc = known(dv.location) or self.locate(value_re(name[-1]))
        return Body(self.qual(*name), dv.expr, loc)

    def named(self) -> Iterator[Body]:
        """Yield the values the author named, without the `$` helpers damlc generates."""
        for dv in self.module.values:
            if not dv.name_with_type.name[-1].startswith("$"):
                yield self.own_body(dv)

    def values(self, alias: dict[lf.ValName, Body]) -> Iterator[Body]:
        for dv in self.module.values:
            name = dv.name_with_type.name
            parent = alias.get(lf.ValName(self.ref, name))
            if parent is not None:
                yield Body(parent.owner, dv.expr, parent.loc)
            else:
                yield self.own_body(dv)


class PackageIndex:
    def __init__(self, dar: Dar) -> None:
        self.dar = dar
        self.packages = {p.pkg_id: p for p in dar.packages}
        self.values: dict[lf.ValName, lf.DefValue] = {}
        self.templates: dict[lf.TypeConName, lf.DefTemplate] = {}
        self.ifaces: dict[lf.TypeConName, lf.DefInterface] = {}
        self.impls: dict[lf.TypeConName, list[Implements]] = {}
        self.exceptions: dict[lf.TypeConName, DefException] = {}
        self.records: dict[lf.TypeConName, tuple[lf.FieldWithType, ...]] = {}
        for pkg in dar.packages:
            scopes = self.scopes(pkg)
            for scope in scopes:
                ref, mod = scope.ref, scope.module
                for data in mod.data_types:
                    if data.record is not None:
                        name = lf.TypeConName(ref, data.name.segments)
                        self.records[name] = tuple(data.record.fields)
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

    def choices(self, pkg: LfPackage | None = None) -> Iterator[ChoiceDecl]:
        scopes = self.scopes(pkg or self.dar.main)
        for scope in scopes:
            yield from scope.choices()

    def arg_fields(self, decl: ChoiceDecl) -> tuple[lf.FieldWithType, ...]:
        """Return the fields of a choice's argument record, or () if it is not a record."""
        typ = decl.choice.arg_binder.type
        if typ.con is None:
            return ()
        return self.records.get(typ.con.tycon, ())

    def reachable(self, root: lf.Expr) -> list[lf.Expr]:
        """Return `root` and the bodies of all main-package values it reaches, each once."""
        found = [root]
        self.follow(root, set(), found)
        return found

    def follow(self, root: lf.Expr, seen: set[lf.ValName], found: list[lf.Expr]) -> None:
        """Append to `found` the bodies of main-package values that `root` refers to."""
        refs = find_all(root, lf.ValName)
        for ref in refs:
            name = ref.node
            if name in seen or not self.is_local(name):
                continue
            seen.add(name)
            body = self.values[name].expr
            found.append(body)
            self.follow(body, seen, found)

    def created_templates(self, root: lf.Expr) -> set[str]:
        """Return the owners (`Module:Template`) of every template `root` may create.

        damlc moves `create` into generated helpers, so main-package helpers are followed.
        """
        owners: set[str] = set()
        bodies = self.reachable(root)
        for body in bodies:
            creates = find_all(body, lf.Update.Create)
            for create in creates:
                owners.add(type_owner(create.node.template))
        return owners

    def is_local(self, name: lf.ValName) -> bool:
        """Return True if `name` is a value defined in the main package."""
        main = package_ref(name) == self.dar.main.pkg_id
        return main and name in self.values

    def template_decls(self, pkg: LfPackage | None = None) -> Iterator[TemplateDecl]:
        scopes = self.scopes(pkg or self.dar.main)
        for scope in scopes:
            yield from scope.template_decls()

    def decls(self, pkg: LfPackage | None = None) -> list[Body]:
        """Return the declaration bodies of a package.

        These are template fields, choices, interface instances and exception messages,
        without the package's top-level values. Defaults to the main package.
        """
        pkg = pkg or self.dar.main
        decls: list[Body] = []
        scopes = self.scopes(pkg)
        for scope in scopes:
            found = scope.decls()
            decls.extend(found)
        extras = extra_bodies(pkg)
        decls.extend(extras)
        return decls

    def bodies(self, pkg: LfPackage | None = None) -> Iterator[Body]:
        """Yield every body of a package: declarations first, then top-level values.

        Compiler helpers reachable from a declaration are reported under that declaration's
        owner and location. Defaults to the main package.
        """
        pkg = pkg or self.dar.main
        decls = self.decls(pkg)
        roots = list(decls)
        scopes = list(self.scopes(pkg))
        for scope in scopes:
            roots.extend(scope.named())
        alias = aliases(roots, pkg, self.values)
        yield from decls
        for scope in scopes:
            yield from scope.values(alias)


def extra_bodies(pkg: LfPackage) -> Iterator[Body]:
    """Yield interface-instance views, methods and exception messages of a package."""
    for impl in pkg.extras.implements:
        owner = f"{impl.template}@{impl.interface}"
        yield Body(f"{owner}.view", impl.view, impl.location)
        methods = impl.methods.items()
        for name, expr in methods:
            yield Body(f"{owner}.{name}", expr, impl.location)
    for exc in pkg.extras.exceptions:
        yield Body(f"{exc.name}.message", exc.message, exc.location)


def aliases(
    decls: Iterable[Body], pkg: LfPackage, values: dict[lf.ValName, lf.DefValue]
) -> dict[lf.ValName, Body]:
    out: dict[lf.ValName, Body] = {}
    todo = deque(decls)
    while todo:
        body = todo.popleft()
        refs = find_all(body.expr, lf.ValName)
        for ref in refs:
            name = ref.node
            if name in out or package_ref(name) != pkg.pkg_id:
                continue
            if module_local_name(name).startswith("$") and name in values:
                out[name] = body
                todo.append(Body(body.owner, values[name].expr, body.loc))
    return out
