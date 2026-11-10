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
from damlisk.lf.builtins import is_time, reads_time
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import ChoiceDecl, PackageIndex
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact


def reads_clock(index: PackageIndex, root: lf.Expr) -> bool:
    """Return True if `root`, or a main-package helper it calls, reads the ledger time."""
    bodies = index.reachable(root)
    for body in bodies:
        refs = find_all(body, lf.ValName)
        for ref in refs:
            if reads_time(ref.node):
                return True
    return False


def caller_times(index: PackageIndex, flow: FieldFlow, decl: ChoiceDecl) -> list[str]:
    """Return the `Time` arguments a choice compares with `<`/`>` without reading ledger time."""
    if decl.iface:
        return []
    times = set()
    fields = index.arg_fields(decl)
    for field in fields:
        if is_time(field.type):
            times.add(field.field)
    if not times:
        return []
    choice = decl.choice
    ordered = flow.ordered(choice.update, choice.arg_binder.var) & times
    if not ordered or reads_clock(index, choice.update):
        return []
    return sorted(ordered)


class TimeFromArgument(AbstractDetector):
    ARGUMENT = "time-from-argument"
    HELP = "Deadline logic on a caller-supplied Time instead of ledger time"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Time from argument"
    WIKI_DESCRIPTION = (
        "A choice compares a `Time` taken from its argument with `<`, `<=`, `>` or `>=` and "
        "never reads the ledger time (`getTime`, `isLedgerTimeLT`, `assertWithinDeadline`, ...). "
        'The controller chooses what "now" is, so deadlines and lock periods are not enforced.'
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`choice Claim with now : Time do assertMsg "locked" (now >= unlock)`: the owner '
        "submits `now = unlock` on day one and claims the vested amount immediately."
    )
    WIKI_RECOMMENDATION = (
        "Read the ledger time: `now <- getTime`, or better `assertDeadlineExceeded` / "
        "`assertWithinDeadline` / `isLedgerTimeGE`, which also work with time bounds."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice that orders caller-supplied times without reading the clock."""
        flow = FieldFlow(self.index.values)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            times = caller_times(self.index, flow, decl)
            if times:
                names = ", ".join(f"`{name}`" for name in times)
                message = f"{decl.owner}: compares caller-supplied time {names}, not ledger time"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
