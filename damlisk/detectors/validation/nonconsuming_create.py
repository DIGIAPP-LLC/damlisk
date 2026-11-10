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
from damlisk.lf.index import ChoiceDecl, PackageIndex
from damlisk.output.finding import Confidence, Finding, Impact


def duplicates_self(decl: ChoiceDecl, index: PackageIndex, flow: FieldFlow) -> bool:
    """Return True if a nonconsuming choice creates its own template and never uses `self`.

    Using `self` covers `archive self` and `exercise self Archive`; without it the
    original contract stays active next to the new one.
    """
    choice = decl.choice
    if decl.iface or choice.consuming:
        return False
    created = index.created_templates(choice.update)
    if decl.parent not in created:
        return False
    used = flow.fields(choice.update, choice.self_binder)
    return not used


class NonconsumingCreate(AbstractDetector):
    ARGUMENT = "nonconsuming-create"
    HELP = "Nonconsuming choice creates its own template without archiving self"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Nonconsuming self-create"
    WIKI_DESCRIPTION = (
        "A `nonconsuming` choice creates a new contract of its own template but never archives "
        "`self`. The original contract stays active, so the asset is duplicated, signed with "
        "the authority of every signatory of the original."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`nonconsuming choice Split with part do create this with amount = part; create this "
        "with amount = amount - part`: the owner splits 100 into 30 + 70 and still holds the "
        "100, so each split mints new tokens co-signed by the issuer."
    )
    WIKI_RECOMMENDATION = (
        "Make the choice consuming (the default), or call `archive self` before creating the "
        "replacement contracts."
    )

    def _detect(self) -> list[Finding]:
        """Report each nonconsuming choice that duplicates its own contract."""
        flow = FieldFlow(self.index.values)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            if duplicates_self(decl, self.index, flow):
                message = f"{decl.owner}: creates `{decl.parent}` but never archives `self`"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
