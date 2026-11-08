from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.detectors.assets.stuck_asset import HOLDERS
from damlisk.lf.flow import THIS, WHOLE, Assign, FieldFlow
from damlisk.lf.index import ChoiceDecl, PackageIndex
from damlisk.output.finding import Confidence, Finding, Impact


def granted(
    index: PackageIndex, flow: FieldFlow, decl: ChoiceDecl, signers: set[str]
) -> list[Assign]:
    """Return the assets a choice builds whose owner comes from an unchecked argument.

    A controller who holds or signs the current contract already has the authority to move
    it, so such a choice is not reported. Neither is an owner taken from the controller, a
    compared argument or a fetched contract, nor a choice whose argument controller is
    compared. A controller passed into an exercise pays from their own assets, so that
    choice is skipped too.
    """
    choice = decl.choice
    if decl.iface:
        return []
    ctrl = flow.fields(choice.controllers, decl.param)
    if ctrl & (HOLDERS | signers):
        return []
    arg = choice.arg_binder.var
    arg_ctrl = flow.fields(choice.controllers, arg)
    usage = flow.fetch_usage(choice.update, arg, decl.param)
    if arg_ctrl & (usage.compared | usage.called):
        return []
    if ctrl & flow.called(choice.update, decl.param):
        return []
    skipped = WHOLE | {THIS} | usage.compared | usage.fetched | arg_ctrl
    found = []
    for item in usage.assigned:
        asset = item.template in index.templates and item.field in HOLDERS
        if asset and item.source not in skipped:
            found.append(item)
    return sorted(found, key=lambda item: (item.source, item.field))


class ArbitraryParty(AbstractDetector):
    ARGUMENT = "value-to-arbitrary-party"
    HELP = "Asset created for an owner from the choice argument by a non-owner controller"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Value to arbitrary party"
    WIKI_DESCRIPTION = (
        "A choice creates an asset, a template with an `owner` or `holder` field, and sets that "
        "field from the choice argument. Its controller neither holds nor signs the current "
        "contract, so a party with no claim on the asset decides who receives it."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`choice Transfer with requester; newOwner controller requester do create this with "
        "owner = newOwner`: anyone who can see the asset moves it to any party."
    )
    WIKI_RECOMMENDATION = (
        "Make the current owner or a signatory the controller, or check the new owner against "
        "parties stored on the contract."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice that sends an asset to an owner taken from its argument."""
        flow = FieldFlow(self.index.values)
        signers = self.signers(flow)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            items = granted(self.index, flow, decl, signers.get(decl.parent, set()))
            for item in items:
                message = f"{decl.owner}: argument `{item.source}` sets `{item.field}` of the asset"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
