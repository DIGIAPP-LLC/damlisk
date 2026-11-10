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

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.detectors.validation.missing_amount import ensure_condition
from damlisk.lf.builtins import bool_const, is_int, is_numeric, is_time, untyped
from damlisk.lf.flow import FieldFlow, peel
from damlisk.lf.index import TemplateDecl
from damlisk.output.finding import Confidence, Finding, Impact


def guarded_fields(decl: TemplateDecl) -> list[str]:
    """Return the `Numeric`, `Int` and `Time` fields of a template."""
    names = []
    for field in decl.fields:
        typ = field.type
        if is_numeric(typ) or is_int(typ) or is_time(typ):
            names.append(field.field)
    return names


def trivial_ensure(flow: FieldFlow, decl: TemplateDecl) -> bool:
    """Return True if the template has no `ensure` or only `ensure True`.

    damlc compiles both to `$censure = \\this -> True`.
    """
    condition = ensure_condition(decl.template)
    if condition is None:
        return True
    if condition.app is not None:
        helper = flow.helper(condition.app.fun, frozenset())
        if helper is not None:
            condition = peel(helper.body)
    return bool_const(untyped(condition)) == "True"


class MissingEnsure(AbstractDetector):
    ARGUMENT = "missing-ensure"
    HELP = "Template with amount or time fields and no ensure"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Missing ensure"
    WIKI_DESCRIPTION = (
        "A template has `Numeric`, `Int` or `Time` fields but no `ensure` clause, or only "
        "`ensure True`. The ledger then accepts contracts with any value in them: negative "
        "amounts, zero counts, inverted time windows."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`template Holding with owner : Party; amount : Decimal where signatory owner`: a "
        "holding with `amount = -100.0` can be created, and every choice that sums holdings "
        "is off by it."
    )
    WIKI_RECOMMENDATION = (
        "Add an `ensure` that states the template invariants, e.g. `ensure amount > 0.0` or "
        "`ensure start < end`."
    )

    def _detect(self) -> list[Finding]:
        """Report each template with amount or time fields and a missing or trivial ensure."""
        flow = FieldFlow(self.index.values)
        findings = []
        decls = self.index.template_decls()
        for decl in decls:
            fields = guarded_fields(decl)
            if fields and trivial_ensure(flow, decl):
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: no ensure constrains {names}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
