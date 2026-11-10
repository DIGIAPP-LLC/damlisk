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
from damlisk.lf.builtins import mentions_update
from damlisk.lf.tree import find_all, used_later
from damlisk.output.finding import Confidence, Finding, Impact


def wrapped_actions(binding: lf.Binding) -> bool:
    """Return True if `binding` binds `pure x` where `x` holds ledger actions (`Update`)."""
    update = binding.bound.update
    if update is None or update.pure is None:
        return False
    return mentions_update(update.pure.type)


def discarded_count(block: lf.Block) -> int:
    """Return how many bindings of `block` wrap ledger actions in `pure` and never use them."""
    count = 0
    for pos, binding in enumerate(block.bindings):
        if wrapped_actions(binding) and not used_later(block, pos, binding.binder.var):
            count += 1
    return count


class DiscardedUpdate(AbstractDetector):
    ARGUMENT = "discarded-update"
    HELP = "Ledger actions wrapped in pure and never run"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Discarded update"
    WIKI_DESCRIPTION = (
        "A `do` block binds `pure x` where `x` contains ledger actions (`Update`, e.g. "
        "`map archive cids`) and never uses the result. The actions are built but never run; "
        "damlc compiles this without a warning and the choice silently does nothing."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`choice BurnAll do _ <- pure (map archive cids); pure ()` succeeds, the caller sees a "
        "committed transaction, but no coin is archived."
    )
    WIKI_RECOMMENDATION = (
        "Run the actions: `forA_ cids archive`, `mapA_ archive cids` or "
        "`sequence_ (map archive cids)`; use `foldlA` instead of `foldl` when the step is "
        "an Update."
    )

    def _detect(self) -> list[Finding]:
        """Report each body that wraps ledger actions in `pure` and drops them."""
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            blocks = find_all(body.expr, lf.Block, body.loc)
            for block in blocks:
                if discarded_count(block.node):
                    message = f"{body.owner}: ledger actions wrapped in `pure` are never run"
                    findings.append(self.finding(body.owner, message, block.loc))
        return findings
