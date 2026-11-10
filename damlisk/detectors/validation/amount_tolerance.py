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
from damlisk.lf.builtins import abs_name, numeric_lit, order_name
from damlisk.lf.flow import FieldFlow
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact


def tolerance(flow: FieldFlow, call: lf.Expr.App) -> str | None:
    """Return the tolerance of `abs (a - b) < 0.0001` as text, or None for other calls."""
    if flow.resolve(call.fun, order_name) is None:
        return None
    absolute = False
    limits = []
    args = flow.call_args(call)
    for arg in args:
        if arg.app is not None and flow.resolve(arg.app.fun, abs_name) is not None:
            absolute = True
        limit = numeric_lit(arg)
        if limit is not None:
            limits.append(limit)
    if not absolute or not limits:
        return None
    return limits[0]


class AmountTolerance(AbstractDetector):
    ARGUMENT = "amount-tolerance"
    HELP = "Decimal amounts compared with a tolerance instead of exactly"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Amount tolerance"
    WIKI_DESCRIPTION = (
        "Two amounts are accepted as equal when `abs (a - b) < eps`. `Decimal` (`Numeric 10`) "
        "is exact fixed-point arithmetic, so a tolerance is never needed to absorb rounding "
        "noise; it only lets outputs differ from inputs by up to `eps`."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`assertMsg "conserved" (abs (sum outputs - sum inputs) < 0.0001)`: every burn/mint '
        "or split may create 0.0001 extra tokens, and the caller repeats it as often as they "
        "like."
    )
    WIKI_RECOMMENDATION = (
        "Compare amounts exactly (`sum outputs == sum inputs`). If a division leaves a "
        "remainder, assign it explicitly, e.g. to the last output or back to the sender."
    )

    def _detect(self) -> list[Finding]:
        """Report each comparison of an absolute difference with a non-zero literal."""
        flow = FieldFlow(self.index.values)
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            calls = find_all(body.expr, lf.Expr.App, body.loc)
            for call in calls:
                limit = tolerance(flow, call.node)
                if limit is not None:
                    message = f"{body.owner}: amounts compared with tolerance {limit}, not exactly"
                    findings.append(self.finding(body.owner, message, call.loc))
        return findings
