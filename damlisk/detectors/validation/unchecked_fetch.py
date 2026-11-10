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
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import ChoiceDecl
from damlisk.output.finding import Confidence, Finding, Impact


def unchecked_fetches(flow: FieldFlow, decl: ChoiceDecl) -> list[str]:
    """Return the contract-id arguments whose fetched contract is read but never checked.

    A check is a comparison of the fetched data with a field of the contract or another
    argument; comparing only with constants does not count.
    """
    if decl.iface:
        return []
    choice = decl.choice
    usage = flow.fetch_usage(choice.update, choice.arg_binder.var, decl.param)
    return sorted(usage.fetched - usage.linked)


class UncheckedFetch(AbstractDetector):
    ARGUMENT = "unchecked-fetch"
    HELP = "Contract fetched from a choice argument and used without validation"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Unchecked fetch"
    WIKI_DESCRIPTION = (
        "A choice fetches a contract whose id comes from its argument and reads its data, but "
        "never compares that contract with the current contract or the other arguments (issuer, "
        "owner, id). Any contract of the right template is accepted, including one the caller "
        "created or one that belongs to someone else."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`choice Borrow with collateral do tok <- fetch collateral; create Debt with amount = "
        "tok.amount / 2.0`: the borrower issues a worthless `Token` to themselves for 1,000,000 "
        "and borrows 500,000 against it."
    )
    WIKI_RECOMMENDATION = (
        'Check the fetched contract before using it, e.g. `assertMsg "issuer" (tok.issuer == '
        'trusted)` and `assertMsg "owner" (tok.owner == borrower)`, or use a checked fetch '
        "helper such as Splice's `fetchChecked`."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice that uses a fetched argument contract without checking it."""
        flow = FieldFlow(self.index.values)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            fields = unchecked_fetches(flow, decl)
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: fetched contract {names} is used without validation"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
