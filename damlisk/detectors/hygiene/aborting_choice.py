from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import lf_name, untyped
from damlisk.lf.flow import peel
from damlisk.output.finding import Confidence, Finding, Impact

FAILURES = {"ERROR", "FAIL_WITH_STATUS"}


class Aborts:
    def __init__(self, values: dict[lf.ValName, lf.DefValue]) -> None:
        """Remember all package values, so helpers such as `abort` can be followed."""
        self.values = values
        self.known: dict[lf.ValName, bool] = {}

    def expr(self, expr: lf.Expr) -> bool:
        """Return True if evaluating `expr` always throws (`error`, `abort`, `throw`, ...)."""
        expr = peel(untyped(expr))
        if expr.throw is not None:
            return True
        if expr.builtin is not None:
            return lf_name(expr.builtin) in FAILURES
        if expr.val is not None:
            return self.value(expr.val)
        if expr.app is not None:
            return self.expr(expr.app.fun)
        if expr.let is not None:
            return self.expr(expr.let.body)
        if expr.case is not None:
            return self.case(expr.case)
        if expr.update is not None:
            return self.update(expr.update)
        return False

    def value(self, name: lf.ValName) -> bool:
        """Return True if package value `name` always throws once applied."""
        if name in self.known:
            return self.known[name]
        if name not in self.values:
            return False
        self.known[name] = False
        result = self.expr(self.values[name].expr)
        self.known[name] = result
        return result

    def case(self, case: lf.Case) -> bool:
        """Return True if every branch of `case` always throws."""
        if not case.alts:
            return False
        for alt in case.alts:
            if not self.expr(alt.body):
                return False
        return True

    def update(self, update: lf.Update) -> bool:
        """Return True if the ledger action `update` always throws.

        A `do` block throws if any of its statements does, since all of them run.
        """
        if update.embed_expr is not None:
            return self.expr(update.embed_expr.body)
        if update.block is None:
            return False
        for binding in update.block.bindings:
            if self.expr(binding.bound):
                return True
        return self.expr(update.block.body)


class AbortingChoice(AbstractDetector):
    ARGUMENT = "aborting-choice"
    HELP = "Choice that always aborts"
    IMPACT = Impact.INFORMATIONAL
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Aborting choice"
    WIKI_DESCRIPTION = (
        "Every exercise of the choice fails: its body always reaches `error`, `abort`, `fail` "
        "or `throw`, directly or through a helper such as `deprecatedChoice`. The choice is "
        "still part of the template's API, so clients may call it and only learn at "
        "submission time that it cannot succeed."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`choice Withdraw controller owner do error "TODO"` compiles and ships: the owner '
        "has no working way to get the asset back."
    )
    WIKI_RECOMMENDATION = (
        "Implement the choice, or remove it. Choices kept only for upgrade compatibility "
        "should be documented as deprecated and point to their replacement."
    )

    def _detect(self) -> list[Finding]:
        """Report each choice whose body always aborts."""
        aborts = Aborts(self.index.values)
        findings = []
        decls = self.index.choices()
        for decl in decls:
            if aborts.expr(decl.choice.update):
                message = f"{decl.owner}: every exercise aborts"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
