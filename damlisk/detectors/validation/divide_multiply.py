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
from damlisk.lf.builtins import arith_name
from damlisk.lf.flow import FieldFlow
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact


def is_division(flow: FieldFlow, expr: lf.Expr, divided: set[str]) -> bool:
    """Return True if `expr` is `a / b` or a `let` variable bound to one."""
    if expr.var is not None:
        return expr.var in divided
    if expr.app is None:
        return False
    return flow.resolve(expr.app.fun, arith_name) == "/"


def divided_names(flow: FieldFlow, root: lf.Expr) -> set[str]:
    """Return the `let` variables in `root` that hold the result of a division."""
    divided: set[str] = set()
    blocks = find_all(root, lf.Block)
    for block in blocks:
        for binding in block.node.bindings:
            if is_division(flow, binding.bound, divided):
                divided.add(binding.binder.var)
    return divided


def multiplies_quotient(flow: FieldFlow, call: lf.Expr.App, divided: set[str]) -> bool:
    """Return True if `call` multiplies the result of a division."""
    if flow.resolve(call.fun, arith_name) != "*":
        return False
    for arg in call.args:
        if is_division(flow, arg, divided):
            return True
    return False


class DivideBeforeMultiply(AbstractDetector):
    ARGUMENT = "divide-before-multiply"
    HELP = "Result of a division is multiplied, losing precision"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Divide before multiply"
    WIKI_DESCRIPTION = (
        "`(a / b) * c` rounds the quotient to 10 decimal places (`Decimal`) or truncates it "
        "(`Int`) before the multiplication, so the rounding error is multiplied by `c`. "
        "`(a * c) / b` rounds only once."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`let share = stake / total in reward * share`: with `total = 3.0` the share is "
        "rounded down, and on a large `reward` every payout is short. Summed over all stakers, "
        "the payouts no longer add up to `reward`, leaving dust stuck or failing a later "
        "conservation check."
    )
    WIKI_RECOMMENDATION = (
        "Multiply first and divide last (`reward * stake / total`), and assign any remainder "
        "explicitly."
    )

    def _detect(self) -> list[Finding]:
        """Report each multiplication whose operand is the result of a division."""
        flow = FieldFlow(self.index.values)
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            divided = divided_names(flow, body.expr)
            calls = find_all(body.expr, lf.Expr.App, body.loc)
            for call in calls:
                if multiplies_quotient(flow, call.node, divided):
                    message = f"{body.owner}: result of a division is multiplied"
                    findings.append(self.finding(body.owner, message, call.loc))
        return findings
