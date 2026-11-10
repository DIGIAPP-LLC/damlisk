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
from damlisk.lf.builtins import BOOLS, bool_const
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact


def branch(case: lf.Case, con: lf.PrimCon) -> str | None:
    for alt in case.alts:
        if alt.default is not None or alt.prim_con == con:
            return bool_const(alt.body)
    return None


def matches_bool(case: lf.Case) -> bool:
    return any(alt.prim_con in BOOLS for alt in case.alts)


def misuse(case: lf.Case) -> str | None:
    scrut = bool_const(case.scrut)
    if scrut is not None:
        return f"condition is always {scrut}"
    if not matches_bool(case):
        return None
    if_true = branch(case, lf.PrimCon.CON_TRUE)
    if_false = branch(case, lf.PrimCon.CON_FALSE)
    if if_true is None or if_false is None:
        return None
    if if_true == if_false:
        return f"result is always {if_true} regardless of the condition"
    if if_true == "True":
        return "conditional returns its own condition (if c then True else False)"
    return "conditional negates its condition (if c then False else True)"


class BooleanConstant(AbstractDetector):
    ARGUMENT = "boolean-cst"
    HELP = "Misuse of Boolean constant"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Misuse of a Boolean constant"
    WIKI_DESCRIPTION = (
        "Reports Boolean constants used as conditions and conditionals that only return "
        "constants. damlc keeps them in Daml-LF without a warning, so they reach the ledger:\n"
        "- `if True` / `if False`: one branch is dead code; the guarded path never runs.\n"
        "- `check || True`: the guard always passes; `assertMsg`, `ensure` or a controller "
        "check stops validating anything (authorization or balance bypass).\n"
        "- `check && False`: the guard always fails; the choice always aborts, so the "
        "contract can never be archived through it (locked assets, denial of service).\n"
        "- `if check then True else False` (or the negated form): redundant code that "
        "often hides a wrong or inverted condition."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`assertMsg "authorized" (isAdmin || True)` was left from debugging: the assertion '
        "always passes and any controller can withdraw any amount. A `Close` choice "
        'guarded by `assertMsg "closed" (check && False)` always fails, so the owner can '
        "never archive the vault."
    )
    WIKI_RECOMMENDATION = (
        "Remove the constant and use the intended condition; replace "
        "`if c then True else False` with `c` and `if c then False else True` with `not c`."
    )

    def _detect(self) -> list[Finding]:
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            cases = find_all(body.expr, lf.Case, body.loc)
            for case in cases:
                message = misuse(case.node)
                if message:
                    findings.append(self.finding(body.owner, f"{body.owner}: {message}", case.loc))
        return findings
