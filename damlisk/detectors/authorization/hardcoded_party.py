from collections.abc import Sequence
from dataclasses import dataclass

from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import is_compare, lf_name, qual_name, untyped
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact

PREVIEW = 24


@dataclass(frozen=True)
class Callee:
    module: str
    name: str
    builtin: str

    def matches(self, fun: lf.Expr) -> bool:
        """Return True if `fun` is this function, called by name or as its LF builtin."""
        fun = untyped(fun)
        if fun.builtin is not None:
            return lf_name(fun.builtin) == self.builtin
        if fun.val is not None:
            return qual_name(fun.val) == (self.module, self.name)
        return False


FROM_TEXT = Callee("DA.Internal.LF", "partyFromText", "TEXT_TO_PARTY")
TO_TEXT = Callee("DA.Internal.LF", "partyToText", "PARTY_TO_TEXT")


def text_literals(args: Sequence[lf.Expr]) -> list[str]:
    """Return every text literal that appears anywhere inside `args`."""
    texts: list[str] = []
    for arg in args:
        found = find_all(arg, lf.PrimLit)
        for lit in found:
            if lit.node.text is not None:
                texts.append(lit.node.text)
    return texts


def converts_party(args: Sequence[lf.Expr]) -> bool:
    """Return True if one of `args` is a direct `partyToText` call."""
    for arg in args:
        call = arg.app
        if call is not None and TO_TEXT.matches(call.fun):
            return True
    return False


def preview(text: str) -> str:
    """Return `text` quoted and shortened to `PREVIEW` characters for a finding message."""
    if len(text) <= PREVIEW:
        return f'"{text}"'
    return f'"{text[:PREVIEW]}..."'


def misuse(call: lf.Expr.App) -> str | None:
    """Describe how `call` hardcodes a party, or return None if it does not."""
    texts = text_literals(call.args)
    if not texts:
        return None
    literal = preview(texts[0])
    if FROM_TEXT.matches(call.fun):
        return f"party built from text literal {literal}"
    if is_compare(call.fun) and converts_party(call.args):
        return f"party compared with text literal {literal}"
    return None


class HardcodedParty(AbstractDetector):
    ARGUMENT = "hardcoded-party"
    HELP = "Party identity hardcoded as a text literal"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Hardcoded party"
    WIKI_DESCRIPTION = (
        "A party built with `partyFromText` from a text literal (plain or obfuscated), or a "
        "`partyToText` result compared with a text literal. damlc rejects party literals, but "
        "these conversions compile and pin the contract to one party id."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`hidden = fromSome (partyFromText (T.reverse "0221::nedduH"))` used as an observer '
        "or beneficiary silently discloses every contract, or diverts a share of rewards, to a "
        "party that the reader of the source cannot see."
    )
    WIKI_RECOMMENDATION = (
        "Pass parties in as template fields or choice arguments and check them against "
        "signatories; never derive authority or disclosure from text."
    )

    def _detect(self) -> list[Finding]:
        """Report every call that builds or compares a party from a text literal."""
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            calls = find_all(body.expr, lf.Expr.App, body.loc)
            for call in calls:
                message = misuse(call.node)
                if message:
                    findings.append(self.finding(body.owner, f"{body.owner}: {message}", call.loc))
        return findings
