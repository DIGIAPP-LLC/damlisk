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
from damlisk.lf.builtins import hash_name, join_name, text_lit
from damlisk.lf.flow import FieldFlow
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact


def let_values(root: lf.Expr) -> dict[str, lf.Expr]:
    """Return the expression bound to each `let` variable in `root`."""
    bound = {}
    blocks = find_all(root, lf.Block)
    for block in blocks:
        for binding in block.node.bindings:
            if binding.binder.var:
                bound[binding.binder.var] = binding.bound
    return bound


def listed(cons: lf.Expr.Cons) -> list[lf.Expr]:
    """Return the elements of list literal `[a, b]`, keeping a non-empty tail as one element."""
    items = list(cons.front)
    if cons.tail.nil is None:
        items.append(cons.tail)
    return items


def adjacent(parts: list[lf.Expr]) -> bool:
    """Return True if two neighbouring parts are both non-literal, with no separator between."""
    for pos in range(1, len(parts)):
        if text_lit(parts[pos - 1]) is None and text_lit(parts[pos]) is None:
            return True
    return False


class Joins:
    def __init__(self, flow: FieldFlow, bound: dict[str, lf.Expr]) -> None:
        """Remember the helpers and `let` variables used to see through joined text."""
        self.flow = flow
        self.bound = bound

    def parts(self, expr: lf.Expr, seen: frozenset[str] = frozenset()) -> list[lf.Expr]:
        """Return the pieces glued into text `expr` (`a <> b`, `implode [a, b]`), or `[expr]`."""
        if expr.var is not None and expr.var in self.bound and expr.var not in seen:
            return self.parts(self.bound[expr.var], seen | {expr.var})
        if expr.app is None:
            return [expr]
        name = self.flow.resolve(expr.app.fun, join_name)
        args = self.flow.call_args(expr.app)
        if name == "<>":
            return self.many(args, seen)
        if name == "implode" and args and args[-1].cons is not None:
            return self.many(listed(args[-1].cons), seen)
        return [expr]

    def many(self, exprs: list[lf.Expr], seen: frozenset[str]) -> list[lf.Expr]:
        """Return the pieces of each expression in `exprs`, in order."""
        parts = []
        for expr in exprs:
            parts.extend(self.parts(expr, seen))
        return parts

    def collides(self, call: lf.Expr.App) -> bool:
        """Return True if `call` hashes text joined from adjacent non-literal parts."""
        if self.flow.resolve(call.fun, hash_name) is None:
            return False
        args = self.flow.call_args(call)
        if not args:
            return False
        return adjacent(self.parts(args[-1]))


class HashConcatCollision(AbstractDetector):
    ARGUMENT = "hash-concat-collision"
    HELP = "Hash of texts joined without a separator"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Hash concat collision"
    WIKI_DESCRIPTION = (
        "`sha256` (or `keccak256`) is applied to texts glued together with `<>` or `implode` "
        "and no separator between two variable parts. Different inputs then give the same "
        'text and the same hash: `"ab" <> "c"` and `"a" <> "bc"` are both `"abc"`.'
    )
    WIKI_EXPLOIT_SCENARIO = (
        "A voucher stores `sha256 (code <> batch)` and redeems on a matching hash. A holder of "
        'code `"12"` in batch `"3"` shares the hash of code `"1"` in batch `"23"`, so one '
        "secret opens both vouchers."
    )
    WIKI_RECOMMENDATION = (
        'Put a separator that cannot occur in the parts between them (`intercalate "|"`), or '
        "prefix each part with its length; hash parts that may contain the separator first."
    )

    def _detect(self) -> list[Finding]:
        """Report each hash of text joined from adjacent non-literal parts."""
        flow = FieldFlow(self.index.values)
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            joins = Joins(flow, let_values(body.expr))
            calls = find_all(body.expr, lf.Expr.App, body.loc)
            for call in calls:
                if joins.collides(call.node):
                    message = f"{body.owner}: hashed text joins parts without a separator"
                    findings.append(self.finding(body.owner, message, call.loc))
        return findings
