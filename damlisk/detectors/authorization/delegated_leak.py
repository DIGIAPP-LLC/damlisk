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
from damlisk.lf.builtins import is_int, is_numeric, is_party
from damlisk.lf.flow import WHOLE, FieldFlow
from damlisk.lf.index import ChoiceDecl, PackageIndex, TemplateDecl
from damlisk.output.finding import Confidence, Finding, Impact

WRAPPERS = (lf.PrimType.LIST, lf.PrimType.OPTIONAL)


def party_or_amount(typ: lf.Type) -> bool:
    """Return True for `Party`, `Numeric` and `Int`, also inside a list or `Optional`."""
    if typ.prim is not None and typ.prim.prim in WRAPPERS and typ.prim.args:
        typ = typ.prim.args[0]
    return is_party(typ) or is_numeric(typ) or is_int(typ)


def ensured(flow: FieldFlow, tmpl: TemplateDecl) -> set[str]:
    """Return the fields of a template that its `ensure` clause reads."""
    precond = tmpl.template.precond
    if precond is None:
        return set()
    used = flow.fields(precond, tmpl.template.param)
    return used - WHOLE


class LeakCheck:
    def __init__(self, index: PackageIndex) -> None:
        """Collect the signatory and `ensure` fields of every template in the main package."""
        self.index = index
        self.flow = FieldFlow(index.values)
        self.signers: dict[str, set[str]] = {}
        self.ensures: dict[str, set[str]] = {}
        tmpls = index.template_decls()
        for tmpl in tmpls:
            self.ensures[tmpl.owner] = ensured(self.flow, tmpl)
            sigs = tmpl.template.signatories
            if sigs is not None:
                self.signers[tmpl.owner] = self.flow.fields(sigs, tmpl.template.param)

    def risky(self, decl: ChoiceDecl, created: set[str]) -> set[str]:
        """Return the party and amount argument fields not read by a created template's `ensure`."""
        names = set()
        fields = self.index.arg_fields(decl)
        for field in fields:
            if party_or_amount(field.type):
                names.add(field.field)
        for owner in created:
            names -= self.ensures.get(owner, set())
        return names

    def cosigned(self, created: set[str], parties: set[str]) -> bool:
        """Return True if a controller field is also a signatory field of a created template."""
        for owner in created:
            if self.signers.get(owner, set()) & parties:
                return True
        return False

    def leaked(self, decl: ChoiceDecl) -> list[str]:
        """Return the parties and amounts a non-signatory controller puts into a signed action.

        The action counts as signed when it also carries contract data other than the
        controller's own fields: a signatory party or a contract id the signatories stored.
        Creates the controller signs too, and exercises the controller is passed into, act
        on the controller's own behalf and are skipped. Arguments the choice compares or
        bounds, and arguments that name the controller, are not reported.
        """
        choice = decl.choice
        if decl.iface:
            return []
        flow = self.flow
        update = choice.update
        ctrl = flow.fields(choice.controllers, decl.param)
        if ctrl & self.signers.get(decl.parent, set()):
            return []
        this_made = flow.created(update, decl.param)
        this_call = flow.called(update, decl.param)
        if not (this_made | this_call) - ctrl:
            return []
        arg = choice.arg_binder.var
        arg_ctrl = flow.fields(choice.controllers, arg)
        created = self.index.created_templates(update)
        found: set[str] = set()
        if not self.cosigned(created, ctrl | arg_ctrl):
            found |= flow.created(update, arg)
        arg_call = flow.called(update, arg)
        if not (this_call & ctrl or arg_call & arg_ctrl):
            found |= arg_call
        checked = flow.compared(update, arg) | flow.ordered(update, arg)
        risky = self.risky(decl, created)
        return sorted((found & risky) - checked - arg_ctrl)


class DelegatedLeak(AbstractDetector):
    ARGUMENT = "delegated-authority-leak"
    HELP = "Non-signatory controller passes parties or amounts into a create or exercise"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Delegated authority leak"
    WIKI_DESCRIPTION = (
        "A choice runs with the authority of the contract signatories, but its controller is "
        "not one of them. When the choice creates or exercises with parties or amounts taken "
        "from the choice argument, the controller makes the signatories sign whatever "
        "contract or exercise they choose."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`signatory issuer; observer holder; nonconsuming choice Mint with value controller "
        "holder do create Token with issuer; owner = holder; amount = value`: the holder mints "
        "tokens of any amount, each signed by the issuer."
    )
    WIKI_RECOMMENDATION = (
        "Take parties and amounts from contract fields the signatories agreed to, bound and "
        "check every argument before it is used (`assertMsg`, `ensure`), or make a signatory "
        "the controller."
    )

    def _detect(self) -> list[Finding]:
        """Report each non-signatory choice that sends parties or amounts into a signed action."""
        check = LeakCheck(self.index)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            fields = check.leaked(decl)
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: argument {names} used with the signatories' authority"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
