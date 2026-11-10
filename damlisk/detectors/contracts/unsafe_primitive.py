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

from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import unsafe_name
from damlisk.lf.index import Body
from damlisk.lf.tree import all_terms
from damlisk.output.finding import Confidence, Finding, Impact

GENERATED = ("$fHasFromAny", "$fHasFromInterface")


def generated(body: Body) -> bool:
    """Return True if `body` is compiler wiring rather than code the author wrote.

    That is a class instance dictionary (a struct of method references, reported under the
    choice that uses it) or a `HasFromAny*` / `HasFromInterface*` instance damlc generates
    for every template.
    """
    if body.expr.struct_con is not None:
        return True
    for prefix in GENERATED:
        if prefix in body.owner:
            return True
    return False


class UnsafePrimitive(AbstractDetector):
    ARGUMENT = "unsafe-primitive"
    HELP = "Unchecked cast of a contract id, interface or Any value"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Unsafe primitive"
    WIKI_DESCRIPTION = (
        "`coerceContractId`, `unsafeFromInterface` and `fromAny` change the static type of a "
        "contract id or value without checking it. The code then trusts a template type the "
        "ledger never confirmed."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`exercise (coerceContractId cid : ContractId Holding) Transfer` on a `cid` the caller "
        "supplies: the choice treats the contract as a `Holding` of this package, while the "
        "caller passed a contract of another template."
    )
    WIKI_RECOMMENDATION = (
        "Use the checked forms: `fromInterface` with a `case` on the result, `fetchFromInterface`"
        " or `fromAnyTemplate`, and fetch the contract to confirm its template before using it."
    )

    def _detect(self) -> list[Finding]:
        """Report each unsafe cast in code the package author wrote."""
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            if generated(body):
                continue
            terms = all_terms(body.expr, body.loc)
            for term in terms:
                if not isinstance(term.node, lf.Expr):
                    continue
                name = unsafe_name(term.node)
                if name is not None:
                    message = f"{body.owner}: unsafe primitive `{name}`"
                    findings.append(self.finding(body.owner, message, term.loc))
        return findings
