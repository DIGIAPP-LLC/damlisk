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
from damlisk.lf.builtins import cid_template, type_owner
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import ChoiceDecl, PackageIndex
from damlisk.output.finding import Confidence, Finding, Impact


def own_inputs(index: PackageIndex, decl: ChoiceDecl) -> set[str]:
    """Return the argument fields that hold contract ids of the choice's own template."""
    inputs = set()
    fields = index.arg_fields(decl)
    for field in fields:
        tycon = cid_template(field.type)
        if tycon is not None and type_owner(tycon) == decl.parent:
            inputs.add(field.field)
    return inputs


def unconsumed_inputs(index: PackageIndex, flow: FieldFlow, decl: ChoiceDecl) -> list[str]:
    """Return the own-template inputs a choice uses but never archives, while creating
    a new contract of that template."""
    if decl.iface:
        return []
    inputs = own_inputs(index, decl)
    if not inputs:
        return []
    choice = decl.choice
    if decl.parent not in index.created_templates(choice.update):
        return []
    arg = choice.arg_binder.var
    used = flow.fields(choice.update, arg) & inputs
    consumed = flow.consumed(choice.update, arg)
    return sorted(used - consumed)


class UnconsumedInput(AbstractDetector):
    ARGUMENT = "unconsumed-input"
    HELP = "Input contract of the same template read but not archived"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Unconsumed input"
    WIKI_DESCRIPTION = (
        "A choice takes contract ids of its own template as input (`other : ContractId Token`, "
        "`others : [ContractId Token]`), uses them, and creates a new contract of that "
        "template, but never archives or exercises the inputs. The inputs stay active, so "
        "their value is counted twice."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`choice Merge with other do tok <- fetch other; create this with amount = amount + "
        "tok.amount`: the owner merges the same 100-token contract into a new one over and "
        "over, minting 100 tokens each time."
    )
    WIKI_RECOMMENDATION = (
        "Archive every input after reading it (`archive other`, `forA_ others archive`), or "
        "exercise a consuming choice on it."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice that folds own-template inputs into a new contract without
        archiving them."""
        flow = FieldFlow(self.index.values)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            fields = unconsumed_inputs(self.index, flow, decl)
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: input {names} is read but never archived"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
