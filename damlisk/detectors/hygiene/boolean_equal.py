from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import bool_const, eq_operator
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact


def misuse(app: lf.Expr.App) -> str | None:
    op = eq_operator(app.fun)
    consts = [bool_const(arg) for arg in app.args if bool_const(arg) is not None]
    if op is None or not consts:
        return None
    const = consts[0]
    keeps = (op == "==") == (const == "True")
    fix = "x" if keeps else "not x"
    return f"comparison with a Boolean constant (x {op} {const}), use `{fix}`"


class BooleanEqual(AbstractDetector):
    ARGUMENT = "boolean-equal"
    HELP = "Comparison to a Boolean constant"
    IMPACT = Impact.INFORMATIONAL
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Comparison to a Boolean constant"
    WIKI_DESCRIPTION = (
        "Detects `==` and `/=` with `True` or `False` as an operand. damlc compiles them to "
        "the `EQUAL` builtin or the `Eq Bool` instance without a warning."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`assertMsg "already used" (used == False)` works, but double negations such as '
        "`active /= False` make inverted guards easy to miss in review."
    )
    WIKI_RECOMMENDATION = (
        "Use the Boolean directly: `x` instead of `x == True`, `not x` instead of `x == False`."
    )

    def _detect(self) -> list[Finding]:
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            calls = find_all(body.expr, lf.Expr.App, body.loc)
            for call in calls:
                message = misuse(call.node)
                if message:
                    findings.append(self.finding(body.owner, f"{body.owner}: {message}", call.loc))
        return findings
