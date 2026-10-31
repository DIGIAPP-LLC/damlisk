import re

from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.util import module_local_name, module_name

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import bool_const, demangle, lf_name
from damlisk.lf.walk import walk
from damlisk.output.finding import Confidence, Finding, Impact

EQ_MODULE = "GHC.Classes"
EQ_RE = re.compile(r"^(?:\$c)?(==|/=)\d*$")


def operator(fun: lf.Expr) -> str | None:
    while isinstance(tyapp := fun.ty_app, lf.Expr.TyApp):
        fun = tyapp.expr
    if fun.builtin is not None:
        return "==" if lf_name(fun.builtin) == "EQUAL" else None
    val = fun.val
    if isinstance(val, lf.ValName) and str(module_name(val)) == EQ_MODULE:
        match = EQ_RE.match(demangle(module_local_name(val)))
        return match[1] if match else None
    return None


def misuse(app: lf.Expr.App) -> str | None:
    op = operator(app.fun)
    const = next((c for a in app.args if (c := bool_const(a)) is not None), None)
    if op is None or const is None:
        return None
    fix = "x" if (op == "==") == (const == "True") else "not x"
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
        return [
            self.finding(body, f"{body.owner}: {message}", visit.loc)
            for body in self.index.bodies()
            for visit in walk(body.expr, body.loc)
            if isinstance(visit.value, lf.Expr.App) and (message := misuse(visit.value))
        ]
