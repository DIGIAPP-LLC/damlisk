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
from damlisk.lf.builtins import loop_name
from damlisk.lf.flow import FieldFlow
from damlisk.lf.tree import all_terms
from damlisk.output.finding import Confidence, Finding, Impact

OPS: dict[type, str] = {
    lf.Update.Create: "create",
    lf.Update.CreateInterface: "create",
    lf.Update.Exercise: "exercise",
    lf.Update.ExerciseInterface: "exercise",
    lf.Update.ExerciseByKey: "exercise",
    lf.Update.SoftExercise: "exercise",
    lf.Update.DynamicExercise: "exercise",
    lf.Update.Fetch: "fetch",
    lf.Update.FetchInterface: "fetch",
    lf.Update.SoftFetch: "fetch",
    lf.Update.RetrieveByKey: "fetch",
}
Seen = frozenset[lf.ValName]


class LoopScan:
    def __init__(self, values: dict[lf.ValName, lf.DefValue]) -> None:
        """Remember all package values, so helpers and callbacks can be followed."""
        self.values = values
        self.flow = FieldFlow(values)
        self.done: dict[lf.ValName, set[str]] = {}
        self.inside: dict[lf.ValName, set[str]] = {}

    def ops(self, expr: lf.Expr, seen: Seen = frozenset()) -> set[str]:
        """Return the ledger operations (`create`, `exercise`, `fetch`) that `expr` performs."""
        kinds: set[str] = set()
        terms = all_terms(expr)
        for term in terms:
            node = term.node
            if isinstance(node, lf.Update):
                kind = OPS.get(type(node._Sum_value))
                if kind is not None:
                    kinds.add(kind)
            elif node.val is not None:
                kinds |= self.value_ops(node.val, seen)
        return kinds

    def value_ops(self, name: lf.ValName, seen: Seen) -> set[str]:
        """Return the ledger operations of package value `name`, once per value."""
        if name in self.done:
            return self.done[name]
        if name in seen or name not in self.values:
            return set()
        kinds = self.ops(self.values[name].expr, seen | {name})
        self.done[name] = kinds
        return kinds

    def looped(self, expr: lf.Expr, seen: Seen = frozenset()) -> set[str]:
        """Return the ledger operations that `expr` runs inside a `forA`, `mapA` or fold."""
        kinds: set[str] = set()
        terms = all_terms(expr)
        for term in terms:
            node = term.node
            if not isinstance(node, lf.Expr):
                continue
            if node.app is not None and self.flow.resolve(node.app.fun, loop_name):
                args = self.flow.call_args(node.app)
                for arg in args:
                    kinds |= self.ops(arg)
            elif node.val is not None:
                kinds |= self.value_looped(node.val, seen)
        return kinds

    def value_looped(self, name: lf.ValName, seen: Seen) -> set[str]:
        """Return the looped ledger operations of package value `name`, once per value."""
        if name in self.inside:
            return self.inside[name]
        if name in seen or name not in self.values:
            return set()
        kinds = self.looped(self.values[name].expr, seen | {name})
        self.inside[name] = kinds
        return kinds


class LedgerOpInLoop(AbstractDetector):
    ARGUMENT = "ledger-op-in-loop"
    HELP = "Create, exercise or fetch inside a loop"
    IMPACT = Impact.LOW
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Ledger operation in a loop"
    WIKI_DESCRIPTION = (
        "A choice runs `create`, `exercise` or `fetch` inside the closure of `forA`, `mapA`, "
        "`foldl` or a similar loop. Every iteration adds nodes to the transaction, so a long "
        "list can exceed transaction limits, and one failing iteration (an archived contract, "
        "a failed check) aborts all the others."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`forA_ payees \\(p, a) -> exercise cashCid Pay with to = p; amt = a`: one payee whose "
        "payment fails blocks every other payee, and a long `payees` list makes the "
        "transaction too large to commit."
    )
    WIKI_RECOMMENDATION = (
        "Bound the number of iterations, or split the work into one choice per item so a "
        "single failure only affects that item."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice that runs a ledger operation inside a loop."""
        scan = LoopScan(self.index.values)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            kinds = scan.looped(decl.choice.update)
            if kinds:
                message = f"{decl.owner}: {', '.join(sorted(kinds))} inside a loop"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
