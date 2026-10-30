from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.walk import walk
from damlisk.output.finding import Confidence, Finding, Impact

BOOLS = {lf.PrimCon.CON_TRUE: "True", lf.PrimCon.CON_FALSE: "False"}


def bool_const(expr: lf.Expr) -> str | None:
    return BOOLS.get(expr._Sum_value) if expr._Sum_name == "prim_con" else None


def branch(case: lf.Case, con: lf.PrimCon) -> str | None:
    for alt in case.alts:
        if alt._Sum_name == "default" or (alt._Sum_name == "prim_con" and alt._Sum_value == con):
            return bool_const(alt.body)
    return None


def misuse(case: lf.Case) -> str | None:
    scrut = bool_const(case.scrut)
    if scrut is not None:
        return f"condition is always {scrut}"
    if not any(alt._Sum_name == "prim_con" and alt._Sum_value in BOOLS for alt in case.alts):
        return None
    pair = (branch(case, lf.PrimCon.CON_TRUE), branch(case, lf.PrimCon.CON_FALSE))
    if None in pair:
        return None
    if pair[0] == pair[1]:
        return f"result is always {pair[0]} regardless of the condition"
    if pair == ("True", "False"):
        return "conditional returns its own condition (if c then True else False)"
    return "conditional negates its condition (if c then False else True)"


class BooleanConstant(AbstractDetector):
    ARGUMENT = "boolean-cst"
    HELP = "Misuse of Boolean constant"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Misuse of a Boolean constant"
    WIKI_DESCRIPTION = (
        "Detects conditions that are Boolean constants (`if True`, `check || True`, "
        "`check && False`) and conditionals that only return Boolean constants. damlc keeps "
        "these in Daml-LF without a warning."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`assertMsg "authorized" (isAdmin || True)` was left from debugging: the assertion '
        "always passes and any controller can withdraw."
    )
    WIKI_RECOMMENDATION = "Remove the constant or use the intended condition."

    def _detect(self) -> list[Finding]:
        return [
            self.finding(body, f"{body.owner}: {message}", visit.loc)
            for body in self.index.bodies()
            for visit in walk(body.expr, body.loc)
            if isinstance(visit.value, lf.Case) and (message := misuse(visit.value))
        ]
