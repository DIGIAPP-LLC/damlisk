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
from dataclasses import dataclass

from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.util import module_local_name

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import demangle, type_owner
from damlisk.lf.index import PackageIndex, TemplateDecl
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact

DERIVED_RE = re.compile(
    r"^(\$\$sc_)?\$(fShow|fEq|fOrd|fGetField|fSetField|cshow|c==|c/=|ccompare|c<|c>|cmax|cmin"
    r"|sel:|W[A-Z])"
)
GETTER_RE = re.compile(r"^\$(sel:|fGetField)")


@dataclass(frozen=True)
class FieldRef:
    owner: str
    field: str


def local_name(name: lf.ValName) -> str:
    """Return the demangled local name of a value, e.g. `$c==` for `$$c$u003d$u003d`."""
    return demangle(module_local_name(name))


def projections(root: lf.Expr) -> set[FieldRef]:
    """Return every record field that `root` reads with a direct projection (`x.field`)."""
    refs: set[FieldRef] = set()
    found = find_all(root, lf.Expr.RecProj)
    for proj in found:
        tycon = proj.node.tycon
        if tycon is not None:
            refs.add(FieldRef(type_owner(tycon.tycon), proj.node.field))
    return refs


class FieldReads:
    """Collect the template fields that user-written code of a package reads."""

    def __init__(self, index: PackageIndex) -> None:
        """Remember the index whose main package is analysed."""
        self.index = index

    def user_code(self) -> list[lf.Expr]:
        """Return declaration bodies and the top-level values that the user wrote.

        Derived instances (`Show`, `Eq`, `Ord`, getters, setters) touch every field
        mechanically, so they are left out.
        """
        roots = [body.expr for body in self.index.decls()]
        modules = self.index.dar.main.modules
        for module in modules:
            for value in module.values:
                name = demangle(value.name_with_type.name[-1])
                if not DERIVED_RE.match(name):
                    roots.append(value.expr)
        return roots

    def getters(self, root: lf.Expr) -> list[lf.Expr]:
        """Return the bodies of the field getters (`$sel:`, `GetField`) that `root` calls."""
        bodies: list[lf.Expr] = []
        refs = find_all(root, lf.ValName)
        for ref in refs:
            value = self.index.values.get(ref.node)
            if value is not None and GETTER_RE.match(local_name(ref.node)):
                bodies.append(value.expr)
        return bodies

    def collect(self) -> set[FieldRef]:
        """Return all fields read by user code, directly or through a getter."""
        reads: set[FieldRef] = set()
        roots = self.user_code()
        for root in roots:
            reads |= projections(root)
            getters = self.getters(root)
            for getter in getters:
                reads |= projections(getter)
        return reads


def unused_fields(decl: TemplateDecl, reads: set[FieldRef]) -> list[str]:
    """Return the fields of a template that no user code reads."""
    unused: list[str] = []
    for field in decl.fields:
        ref = FieldRef(decl.owner, field.field)
        if ref not in reads:
            unused.append(field.field)
    return unused


class UnusedTemplateField(AbstractDetector):
    ARGUMENT = "unused-template-field"
    HELP = "Template field that no ledger code reads"
    IMPACT = Impact.INFORMATIONAL
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Unused template field"
    WIKI_DESCRIPTION = (
        "A template field that no `ensure`, signatory, observer, key, choice, interface view or "
        "helper reads. It is stored and disclosed on every contract but never enforced."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`template Shop with currency : Text` suggests payments are limited to one token, but "
        "`Buy` never compares the paid token with it, so any token is accepted."
    )
    WIKI_RECOMMENDATION = (
        'Enforce the field where it matters (for example `assertMsg "token" (paid == '
        "currency)`) or remove it."
    )

    def _detect(self) -> list[Finding]:
        """Report each template with fields that user code never reads."""
        reads = FieldReads(self.index).collect()
        findings = []
        decls = self.index.template_decls()
        for decl in decls:
            unused = unused_fields(decl, reads)
            if unused:
                names = ", ".join(f"`{name}`" for name in unused)
                message = f"{decl.owner}: no code reads {names}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
