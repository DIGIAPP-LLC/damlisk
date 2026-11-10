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
from damlisk.lf.index import ChoiceDecl, TemplateDecl
from damlisk.output.finding import Confidence, Finding, Impact

HOLDERS = frozenset({"owner", "holder"})


def holder_fields(decl: TemplateDecl) -> set[str]:
    """Return the `owner` and `holder` fields of a template."""
    names = {field.field for field in decl.fields}
    return names & HOLDERS


def stuck(flow: FieldFlow, decl: TemplateDecl, choices: list[ChoiceDecl]) -> list[str]:
    """Return the holder fields of a template when none controls a consuming choice.

    `Archive` does not count: it is controlled by all signatories, not by the holder.
    """
    holders = holder_fields(decl)
    if not holders:
        return []
    for choice in choices:
        ch = choice.choice
        if ch.consuming and ch.name != "Archive":
            ctrl = flow.fields(ch.controllers, choice.param)
            if ctrl & holders:
                return []
    return sorted(holders)


class StuckAsset(AbstractDetector):
    ARGUMENT = "stuck-asset"
    HELP = "Asset its owner cannot move: no owner-controlled consuming choice"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Stuck asset"
    WIKI_DESCRIPTION = (
        "A template with an `owner` or `holder` field has no consuming choice, other than "
        "`Archive`, that this party controls. The holder cannot transfer, split or redeem the "
        "asset alone; only other parties can move it."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`template Holding with issuer; owner; amount` whose only choice is `Freeze` controlled "
        "by the issuer: the owner holds the amount but can never transfer it, and the issuer "
        "decides when, or whether, it moves."
    )
    WIKI_RECOMMENDATION = (
        "Give the holder a consuming choice (`Transfer`, `Redeem`, `Split`) or document the "
        "contract, often a rules contract, through which the holder moves the asset."
    )

    def _detect(self) -> list[Finding]:
        """Report each template whose holder controls no consuming choice except `Archive`."""
        flow = FieldFlow(self.index.values)
        by_parent: dict[str, list[ChoiceDecl]] = {}
        decls = self.index.choices()
        for decl in decls:
            by_parent.setdefault(decl.parent, []).append(decl)
        findings = []
        tmpls = self.index.template_decls()
        for tmpl in tmpls:
            fields = stuck(flow, tmpl, by_parent.get(tmpl.owner, []))
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{tmpl.owner}: {names} controls no consuming choice except Archive"
                findings.append(self.finding(tmpl.owner, message, tmpl.loc))
        return findings
