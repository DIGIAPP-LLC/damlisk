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
from damlisk.detectors.loops.ledger_op_in_loop import LoopScan
from damlisk.lf.builtins import is_list
from damlisk.lf.flow import SIZE, FieldFlow
from damlisk.lf.index import ChoiceDecl, PackageIndex
from damlisk.output.finding import Confidence, Finding, Impact


def list_fields(index: PackageIndex, decl: ChoiceDecl) -> set[str]:
    """Return the fields of a choice argument that hold a list."""
    fields = index.arg_fields(decl)
    return {field.field for field in fields if is_list(field.type)}


def unbounded(index: PackageIndex, flow: FieldFlow, decl: ChoiceDecl) -> list[str]:
    """Return the argument lists that a ledger loop runs over without a `length` check."""
    choice = decl.choice
    usage = flow.loops(choice.update, choice.arg_binder.var)
    fields = usage.looped & list_fields(index, decl)
    return sorted(name for name in fields if SIZE + name not in usage.ordered)


class UnboundedInputLoop(AbstractDetector):
    ARGUMENT = "unbounded-input-loop"
    HELP = "Loop over a list from the choice argument with no length check"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Unbounded input loop"
    WIKI_DESCRIPTION = (
        "A choice runs `create`, `exercise` or `fetch` inside `forA`, `mapA`, `foldl` or a "
        "similar loop over a list that comes from the choice argument, and nothing compares "
        "`length` of that list with a limit. "
        "The submitter decides how many iterations run, so the transaction can grow past "
        "the limits of the ledger."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`forA_ payees \\(p, a) -> exercise cashCid Pay with to = p; amt = a` with a `payees` "
        "list of many thousands of entries makes the transaction too large to commit, or "
        "creates that many contracts under the signatories' authority."
    )
    WIKI_RECOMMENDATION = (
        'Check the length first, for example `assertMsg "too many" (length payees <= 50)`, '
        "or split the work into several transactions."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice whose ledger loop runs over an unchecked argument list."""
        scan = LoopScan(self.index.values)
        flow = FieldFlow(self.index.values, lengths=True, ledger=scan.ops)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            fields = unbounded(self.index, flow, decl)
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: loop over argument {names} with no length check"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
