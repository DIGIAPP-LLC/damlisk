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
from damlisk.lf.flow import CLOCK, FieldFlow
from damlisk.lf.index import ChoiceDecl
from damlisk.output.finding import Confidence, Finding, Impact


def time_branch(flow: FieldFlow, decl: ChoiceDecl) -> bool:
    """Return True if the ledger time decides a `case`, `if` or assertion in a choice."""
    choice = decl.choice
    branched = flow.branched(choice.update, choice.arg_binder.var, decl.param)
    return CLOCK in branched


class TimeDependence(AbstractDetector):
    ARGUMENT = "time-dependence"
    HELP = "Ledger time decides a branch"
    IMPACT = Impact.LOW
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Time dependence"
    WIKI_DESCRIPTION = (
        "A choice reads the ledger time (`getTime`, `isLedgerTimeLT`, `assertDeadlineExceeded`, "
        "...) and branches on it. The submitting participant picks the ledger time within the "
        "allowed skew, so a deadline or expiry check is decided by the submitter for "
        "transactions near the deadline."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`now <- getTime; assertMsg "closed" (now < closesAt)`: a bidder submits just after '
        "the close with a ledger time inside the skew window and the bid is still accepted."
    )
    WIKI_RECOMMENDATION = (
        "Make sure a deadline tolerates the skew window, keep time windows much longer than the "
        "skew, and never rely on ledger time for ordering or exact instants."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice in which the ledger time decides a branch."""
        flow = FieldFlow(self.index.values, clock=True)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            if time_branch(flow, decl):
                message = f"{decl.owner}: ledger time decides a branch"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
