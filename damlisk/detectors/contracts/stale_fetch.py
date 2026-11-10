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

from dataclasses import dataclass

from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import cid_template, type_args
from damlisk.lf.flow import FieldFlow, peel
from damlisk.lf.index import PackageIndex
from damlisk.lf.tree import find_all, mentions_var
from damlisk.output.finding import Confidence, Finding, Impact


@dataclass(frozen=True)
class Action:
    update: lf.Update
    cid: lf.Expr


@dataclass(frozen=True)
class Stale:
    binder: str
    choice: str


def cid_key(expr: lf.Expr) -> str | None:
    """Return a name for the contract id `expr`: a variable or `record.field`, else None."""
    if expr.var is not None:
        return expr.var
    proj = expr.rec_proj
    if proj is not None and proj.record.var is not None:
        return f"{proj.record.var}.{proj.field}"
    return None


def returns_cid(typ: lf.Type, tycon: lf.TypeConName) -> bool:
    """Return True if `typ` holds a `ContractId` of template `tycon`, also nested."""
    if cid_template(typ) == tycon:
        return True
    nested = type_args(typ)
    for arg in nested:
        if returns_cid(arg, tycon):
            return True
    return False


class StaleScan:
    def __init__(self, index: PackageIndex) -> None:
        """Remember the package, so helpers and choice definitions can be looked up."""
        self.index = index
        self.flow = FieldFlow(index.values)

    def action(self, expr: lf.Expr) -> Action | None:
        """Return the ledger action `expr` runs and its contract id, also through a helper.

        damlc compiles `fetch cid` and `exercise cid C` to helpers that take the contract id
        as a parameter; the argument passed for it is returned.
        """
        if expr.update is not None:
            cid = action_cid(expr.update)
            return None if cid is None else Action(expr.update, cid)
        call = expr.app
        if call is None:
            return None
        helper = self.flow.helper(call.fun, frozenset())
        if helper is None:
            return None
        body = peel(helper.body)
        if body.update is None:
            return None
        cid = action_cid(body.update)
        if cid is None:
            return None
        params = helper.params(len(call.args))
        if cid.var in params:
            cid = call.args[params.index(cid.var)]
        return Action(body.update, cid)

    def successor(self, update: lf.Update) -> str | None:
        """Return the choice name if `update` consumes a contract and returns its successor.

        That is a consuming choice, other than `Archive`, whose result holds a new
        `ContractId` of the same template.
        """
        ex = update.exercise
        if ex is None or ex.choice == "Archive":
            return None
        tmpl = self.index.templates.get(ex.template)
        if tmpl is None:
            return None
        for choice in tmpl.choices:
            if choice.name == ex.choice and choice.consuming:
                if returns_cid(choice.ret_type, ex.template):
                    return choice.name
        return None

    def stale(self, block: lf.Block) -> list[Stale]:
        """Return the fetched values in `block` used after their contract got a successor."""
        found = []
        fetched: dict[str, str] = {}
        bindings = block.bindings
        for pos, binding in enumerate(bindings):
            action = self.action(binding.bound)
            if action is None:
                continue
            key = cid_key(action.cid)
            if key is None:
                continue
            if action.update.fetch is not None:
                fetched[key] = binding.binder.var
                continue
            choice = self.successor(action.update)
            if choice is None or key not in fetched:
                continue
            name = fetched.pop(key)
            later = [b.bound for b in bindings[pos + 1 :]] + [block.body]
            if any(mentions_var(expr, name) for expr in later):
                found.append(Stale(name, choice))
        return found


def action_cid(update: lf.Update) -> lf.Expr | None:
    """Return the contract id a fetch or exercise acts on, or None for other actions."""
    if update.fetch is not None:
        return update.fetch.cid
    if update.exercise is not None:
        return update.exercise.cid
    return None


class StaleFetch(AbstractDetector):
    ARGUMENT = "stale-fetch"
    HELP = "Fetched value used after the contract was replaced by a successor"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Stale fetch"
    WIKI_DESCRIPTION = (
        "A choice fetches a contract, then exercises a consuming choice on the same contract "
        "id that returns a new contract of the same template, and keeps using the fetched "
        "value. The fetched value describes the archived version, not the successor, so it "
        "is out of date. An `Archive` followed by use of the fetched value is the usual "
        "merge pattern and is not reported."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`acc <- fetch cid; _ <- exercise cid Withdraw with amt = 10.0; "
        "create Receipt with remaining = acc.amount`: the receipt shows the balance before "
        "the withdrawal."
    )
    WIKI_RECOMMENDATION = (
        "Fetch the successor contract id returned by the choice, or compute the new values "
        "before the exercise."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice that uses a fetched value after its contract got a successor."""
        scan = StaleScan(self.index)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            found: list[Stale] = []
            bodies = self.index.reachable(decl.choice.update)
            for body in bodies:
                blocks = find_all(body, lf.Block)
                for block in blocks:
                    found.extend(scan.stale(block.node))
            for item in found:
                message = f"{decl.owner}: `{item.binder}` is used after `{item.choice}`"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
