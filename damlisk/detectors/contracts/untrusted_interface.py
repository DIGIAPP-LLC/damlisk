from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import cid_template
from damlisk.lf.flow import WHOLE, FieldFlow
from damlisk.lf.index import ChoiceDecl, PackageIndex
from damlisk.output.finding import Confidence, Finding, Impact


def template_cids(index: PackageIndex, decl: ChoiceDecl) -> set[str]:
    """Return the argument fields declared as the contract id of a concrete template."""
    names = set()
    fields = index.arg_fields(decl)
    for field in fields:
        tycon = cid_template(field.type)
        if tycon is not None and tycon in index.templates:
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
            concrete = template_cids(self.index, decl)
            fields = untrusted_cids(flow, decl, signers.get(decl.parent, set()), concrete)
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: interface contract id from argument {names}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
