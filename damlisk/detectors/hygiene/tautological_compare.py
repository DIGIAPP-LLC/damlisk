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
from damlisk.lf.builtins import eq_operator, order_name
from damlisk.lf.flow import FieldFlow
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact

ALWAYS = {"==": True, "<=": True, ">=": True, "/=": False, "<": False, ">": False}


def same_value(left: lf.Expr, right: lf.Expr) -> bool:
    """Return True if `left` and `right` are the same variable or the same field of one."""
    if left.var is not None:
        return left.var == right.var
    if left.rec_proj is None or right.rec_proj is None:
        return False
    if left.rec_proj.field != right.rec_proj.field:
        return False
    return same_value(left.rec_proj.record, right.rec_proj.record)


def self_compare(flow: FieldFlow, call: lf.Expr.App) -> str | None:
    """Return the operator of `x == x`, `x < x`, ... if `call` compares a value with itself."""
    operator = flow.resolve(call.fun, eq_operator)
    if operator is None:
        operator = flow.resolve(call.fun, order_name)
    if operator is None or len(call.args) != 2:
        return None
    left, right = call.args
    if same_value(left, right):
        return operator
    return None


class TautologicalCompare(AbstractDetector):
    ARGUMENT = "tautological-compare"
    HELP = "Value compared with itself"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Tautological compare"
    WIKI_DESCRIPTION = (
        "A value is compared with itself (`payer == payer`, `price >= price`, `x /= x`). The "
        "result is fixed: `==`, `<=`, `>=` are always True and `/=`, `<`, `>` always False. "
        "It is almost always a typo for another field, so the intended check is missing."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`assertMsg "payer is taker" (payer == payer)` was meant to be `payer == taker`: any '
        "party can be named as payer and the swap settles against their holdings."
    )
    WIKI_RECOMMENDATION = "Compare with the intended value, or remove the check."

    def _detect(self) -> list[Finding]:
        """Report each comparison of a value with itself."""
        flow = FieldFlow(self.index.values)
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            calls = find_all(body.expr, lf.Expr.App, body.loc)
            for call in calls:
                operator = self_compare(flow, call.node)
                if operator is not None:
                    always = ALWAYS[operator]
                    text = f"value compared with itself by `{operator}`, always {always}"
                    message = f"{body.owner}: {text}"
                    findings.append(self.finding(body.owner, message, call.loc))
        return findings
