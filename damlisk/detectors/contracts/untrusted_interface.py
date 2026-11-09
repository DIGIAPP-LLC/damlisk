from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import type_args
from damlisk.lf.flow import WHOLE, FieldFlow
from damlisk.lf.index import ChoiceDecl, PackageIndex
from damlisk.output.finding import Confidence, Finding, Impact


def only_templates(index: PackageIndex, typ: lf.Type, seen: set[lf.TypeConName]) -> bool:
    """Return True if every contract id inside `typ` names a template, searching records."""
    prim = typ.prim
    if prim is not None and prim.prim == lf.PrimType.CONTRACT_ID and prim.args:
        inner = prim.args[0]
        return inner.con is not None and inner.con.tycon in index.templates
    nested = type_args(typ)
    if typ.con is not None and typ.con.tycon not in seen:
        seen.add(typ.con.tycon)
        fields = index.records.get(typ.con.tycon, ())
        nested.extend(field.type for field in fields)
    for arg in nested:
        if not only_templates(index, arg, seen):
            return False
    return True


def concrete_fields(index: PackageIndex, decl: ChoiceDecl) -> set[str]:
    """Return the argument fields that hold no interface contract id, also inside records."""
    names = set()
    fields = index.arg_fields(decl)
    for field in fields:
        if only_templates(index, field.type, set()):
            names.add(field.field)
    return names


def untrusted_cids(
    flow: FieldFlow, decl: ChoiceDecl, signers: set[str], concrete: set[str]
) -> list[str]:
    """Return the argument fields used as interface contract ids, exercised or fetched.

    A controller who is the only signatory risks only their own authority, so such a
    choice is not reported. Fields in `concrete` name one template and are skipped.
    """
    choice = decl.choice
    if decl.iface:
        return []
    ctrl = flow.fields(choice.controllers, decl.param)
    if not signers - ctrl:
        return []
    used = flow.iface_cids(choice.update, choice.arg_binder.var)
    return sorted(used - WHOLE - concrete)


class UntrustedInterface(AbstractDetector):
    ARGUMENT = "untrusted-interface-exercise"
    HELP = "Interface contract id from the choice argument is exercised or fetched"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Untrusted interface exercise"
    WIKI_DESCRIPTION = (
        "A choice exercises or fetches an interface contract whose id comes from the choice "
        "argument. The controller picks the contract, so the implementation behind it can come "
        "from any vetted package, and the signatories of the current contract do not review it."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`choice Settle with holdingCid : ContractId Holding controller trader do exercise "
        "holdingCid Send with receiver`: the trader passes their own template implementing "
        "`Holding`, whose view names the bank as `owner`, so its code runs with the bank's "
        "authority."
    )
    WIKI_RECOMMENDATION = (
        "Store the contract id on the contract, check the implementation's admin against a "
        "trusted party inside a vetted implementation, or exercise a concrete template."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice that exercises or fetches an interface id from its argument."""
        flow = FieldFlow(self.index.values)
        signers = self.signers(flow)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            concrete = concrete_fields(self.index, decl)
            fields = untrusted_cids(flow, decl, signers.get(decl.parent, set()), concrete)
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: interface contract id from argument {names}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
