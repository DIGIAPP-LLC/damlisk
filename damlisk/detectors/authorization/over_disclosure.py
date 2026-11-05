from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.flow import WHOLE, FieldFlow
from damlisk.lf.index import ChoiceDecl
from damlisk.output.finding import Confidence, Finding, Impact


def arg_observers(flow: FieldFlow, decl: ChoiceDecl) -> list[str]:
    """Return the choice argument fields that the choice observers are taken from."""
    observers = decl.choice.observers
    if observers is None:
        return []
    arg = decl.choice.arg_binder.var
    used = flow.fields(observers, arg)
    return sorted(used - WHOLE)


class OverDisclosure(AbstractDetector):
    ARGUMENT = "over-disclosure"
    HELP = "Choice observers taken from the choice argument"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Over-disclosure"
    WIKI_DESCRIPTION = (
        "The choice observers come from choice argument fields. Every party the controller "
        "names there sees the exercise and everything it creates, fetches or exercises, so the "
        "controller can divulge the contract and its consequences to any party."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`choice Settle with watchers : [Party] observer watchers controller owner`: the owner "
        "passes a competitor in `watchers`, and the competitor sees the settled amounts and the "
        "counterparties of every contract the choice touches."
    )
    WIKI_RECOMMENDATION = (
        "Take choice observers from contract fields that the signatories agreed to, or check the "
        "argument parties against an allowed list before they are used as observers."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice whose observers come from choice argument fields."""
        flow = FieldFlow(self.index.values)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            fields = arg_observers(flow, decl)
            if fields:
                names = ", ".join(f"`{name}`" for name in fields)
                message = f"{decl.owner}: choice observers taken from argument {names}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
