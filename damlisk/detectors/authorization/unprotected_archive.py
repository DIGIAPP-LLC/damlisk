from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import ChoiceDecl
from damlisk.output.finding import Confidence, Finding, Impact


def outside_ctrl(flow: FieldFlow, decl: ChoiceDecl, signers: set[str]) -> list[str]:
    """Return the controller fields of a consuming choice when none of them is a signatory."""
    choice = decl.choice
    if decl.iface or not choice.consuming:
        return []
    party_ctrl = flow.fields(choice.controllers, decl.param)
    if party_ctrl & signers:
        return []
    return sorted(party_ctrl)


class UnprotectedArchive(AbstractDetector):
    ARGUMENT = "unprotected-archive"
    HELP = "Consuming choice controlled by a non-signatory"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Unprotected archive"
    WIKI_DESCRIPTION = (
        "A consuming choice is controlled only by contract parties that are not signatories "
        "(observers such as an auditor or a counterparty). Exercising it archives the contract, "
        "so a party that never signed it can destroy it."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`signatory issuer; observer owner, auditor; choice Cancel controller auditor do pure ()`:"
        " the auditor archives the issuer's asset at will."
    )
    WIKI_RECOMMENDATION = (
        "Make the choice `nonconsuming`, add a signatory as co-controller, or make the controller "
        "a signatory. Keep consuming observer choices only where ending the contract is their "
        "purpose (rejecting a proposal) and document it."
    )

    def _detect(self) -> list[Finding]:
        """Report each consuming choice none of whose controllers signs the contract."""
        flow = FieldFlow(self.index.values)
        signers = self.signers(flow)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            fields = outside_ctrl(flow, decl, signers.get(decl.parent, set()))
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: archived by non-signatory controller {names}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
