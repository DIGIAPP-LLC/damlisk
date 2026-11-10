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
from damlisk.lf.flow import FieldFlow, PartialUse
from damlisk.lf.index import ChoiceDecl
from damlisk.output.finding import Confidence, Finding, Impact


def partial_uses(flow: FieldFlow, decl: ChoiceDecl) -> list[PartialUse]:
    """Return the choice-argument fields that reach a partial function, sorted by field."""
    if decl.iface:
        return []
    choice = decl.choice
    uses = flow.partial(choice.update, choice.arg_binder.var)
    return sorted(uses, key=lambda use: (use.field, use.function))


def describe(uses: list[PartialUse]) -> str:
    """Render uses as "`winners` -> head, `price` -> fromSome"."""
    parts = [f"`{use.field}` -> {use.function}" for use in uses]
    return ", ".join(parts)


class PartialFunction(AbstractDetector):
    ARGUMENT = "partial-function"
    HELP = "Choice argument passed to a partial function (head, fromSome, ...)"
    IMPACT = Impact.LOW
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Partial function on choice argument"
    WIKI_DESCRIPTION = (
        "A choice passes data from its argument to a partial function such as `head`, `last`, "
        "`!!`, `fromSome`, `fromJust` or `maximum`. An empty list or `None` aborts the whole "
        "transaction with a generic error."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`choice Payout with winners : [Party] do pure (head winners)`: the controller (or a "
        "delegated workflow) submits `winners = []` and every transaction that includes the "
        "payout fails, blocking settlement."
    )
    WIKI_RECOMMENDATION = (
        "Pattern match on the input or use `fromSomeNote` / `DA.List.Total` / an explicit "
        "`assertMsg` so the failure is intended and explained."
    )

    def _detect(self) -> list[Finding]:
        """Report each template choice whose argument reaches a partial function."""
        flow = FieldFlow(self.index.values)
        findings = []
        choices = self.index.choices()
        for decl in choices:
            uses = partial_uses(flow, decl)
            if uses:
                message = f"{decl.owner}: argument reaches partial function: {describe(uses)}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
