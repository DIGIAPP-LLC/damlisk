from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.flow import CLOCK, HASH, FieldFlow
from damlisk.lf.index import ChoiceDecl
from damlisk.output.finding import Confidence, Finding, Impact


def weak_picks(flow: FieldFlow, decl: ChoiceDecl) -> list[str]:
    """Return how a choice picks an element with the ledger time or a hash.

    A list index from either counts; a map key counts only when it comes from the ledger
    time, because a hash is a common map key that identifies rather than selects.
    """
    choice = decl.choice
    usage = flow.picks(choice.update, choice.arg_binder.var, decl.param)
    picks = []
    if CLOCK in usage.indexed:
        picks.append("ledger time picks a list element")
    if HASH in usage.indexed:
        picks.append("a hash picks a list element")
    if CLOCK in usage.keyed:
        picks.append("ledger time picks a map entry")
    return picks


class WeakRandomness(AbstractDetector):
    ARGUMENT = "weak-randomness"
    HELP = "Ledger time or a hash picks a list element or map entry"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Weak randomness"
    WIKI_DESCRIPTION = (
        "A choice uses the ledger time or a `sha256`/`keccak256` hash as a source of "
        "randomness to pick a list element with `!!`, or uses the ledger time as the key of "
        "a map lookup. The submitter chooses the ledger time "
        "within the skew window and can compute any hash of ledger data in advance, so the "
        "pick is predictable and can be steered."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`now <- getTime; let winner = players !! (micros now started % length players)`: "
        "the host submits the draw with the ledger time that makes their own party win."
    )
    WIKI_RECOMMENDATION = (
        "Do not derive randomness on the ledger. Use a commit-reveal scheme between the "
        "parties or an external randomness source whose result is signed and verified."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice in which the ledger time or a hash picks an element."""
        flow = FieldFlow(self.index.values, clock=True, hashes=True)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            picks = weak_picks(flow, decl)
            if picks:
                message = f"{decl.owner}: {'; '.join(picks)}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
