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


def unchecked_fields(flow: FieldFlow, decl: ChoiceDecl) -> list[str]:
    choice = decl.choice
    if decl.iface or not choice.consuming:
        return []
    party_ctrl = flow.fields(choice.controllers, decl.param)
    if party_ctrl:
        return []
    arg = choice.arg_binder.var
    arg_ctrl = flow.fields(choice.controllers, arg)
    checked = flow.compared(choice.update, arg)
    return sorted(arg_ctrl - checked)


class ControllerFromArgument(AbstractDetector):
    ARGUMENT = "controller-from-argument"
    HELP = "Consuming choice controlled only by an unchecked choice argument"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Controller taken from the choice argument"
    WIKI_DESCRIPTION = (
        "A consuming template choice whose controllers come only from choice argument fields, "
        "and whose body never compares those fields: any party that can see the contract can "
        "exercise it and archive or move the contract."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`choice Transfer with requester : Party; newOwner : Party controller requester` lets an "
        "observer pass itself as `requester` and transfer the asset to itself."
    )
    WIKI_RECOMMENDATION = (
        "Control the choice by a contract party (`controller owner`), add a contract party as a "
        'co-controller, or check the argument (`assertMsg "owner only" (requester == owner)`).'
    )

    def _detect(self) -> list[Finding]:
        flow = FieldFlow(self.index.values)
        findings = []
        choices = self.index.choices()
        for decl in choices:
            fields = unchecked_fields(flow, decl)
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: controlled by unchecked argument {names}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
