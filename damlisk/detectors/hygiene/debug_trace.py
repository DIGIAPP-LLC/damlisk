from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import trace_name
from damlisk.lf.tree import all_terms
from damlisk.output.finding import Confidence, Finding, Impact


class DebugTrace(AbstractDetector):
    ARGUMENT = "debug-trace"
    HELP = "Debug trace left in production code"
    IMPACT = Impact.INFORMATIONAL
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Debug trace"
    WIKI_DESCRIPTION = (
        "`trace`, `traceRaw`, `traceId`, `debug` and `debugRaw` compile to the `TRACE` builtin, "
        "which writes its message to the participant log every time the code runs."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`debug ("withdraw " <> show amount)` in a choice writes every amount to the logs of '
        "each participant that runs it, where operators and log pipelines read data the ledger "
        "keeps private."
    )
    WIKI_RECOMMENDATION = "Remove debug output before release, or keep it in Daml Script tests."

    def _detect(self) -> list[Finding]:
        """Report each debug trace in the package."""
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            terms = all_terms(body.expr, body.loc)
            for term in terms:
                if not isinstance(term.node, lf.Expr):
                    continue
                name = trace_name(term.node)
                if name is not None:
                    message = f"{body.owner}: debug output `{name}`"
                    findings.append(self.finding(body.owner, message, term.loc))
        return findings
