from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import clock_name, eq_operator
from damlisk.lf.flow import FieldFlow
from damlisk.lf.tree import find_all
from damlisk.output.finding import Confidence, Finding, Impact


def reads_now(flow: FieldFlow, bound: lf.Expr) -> bool:
    """Return True if `bound` is `getTime`, inline or through a compiler helper."""
    if bound.update is not None:
        return bound.update.get_time is not None
    if bound.app is not None:
        bound = bound.app.fun
    return flow.resolve(bound, clock_name) is not None


def clock_names(flow: FieldFlow, root: lf.Expr) -> set[str]:
    """Return the variables in `root` that hold the ledger time (`now <- getTime`)."""
    names: set[str] = set()
    blocks = find_all(root, lf.Block)
    for block in blocks:
        for binding in block.node.bindings:
            bound = binding.bound
            if reads_now(flow, bound) or bound.var in names:
                names.add(binding.binder.var)
    return names


def time_equality(flow: FieldFlow, call: lf.Expr.App, names: set[str]) -> str | None:
    """Return `==` or `/=` if `call` tests the ledger time for equality, or None."""
    operator = flow.resolve(call.fun, eq_operator)
    if operator is None:
        return None
    args = flow.call_args(call)
    for arg in args:
        if arg.var is not None and arg.var in names:
            return operator
    return None


class TimeEquality(AbstractDetector):
    ARGUMENT = "time-equality"
    HELP = "Ledger time compared with == or /="
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Time equality"
    WIKI_DESCRIPTION = (
        "The ledger time from `getTime` is compared with `==` or `/=`. Ledger time has "
        "microsecond resolution and is chosen by the submitting participant within a skew "
        "window, so it practically never equals a given instant: `now == t` is always False "
        "and `now /= t` always True."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`now <- getTime; assertMsg "not closed" (now == closesAt)`: the auction can never '
        "be closed. `if now /= closesAt then bid else abort` accepts bids long after the close."
    )
    WIKI_RECOMMENDATION = (
        "Compare with an ordering (`now >= closesAt`), or use `assertDeadlineExceeded` / "
        "`assertWithinDeadline` / `isLedgerTimeGE`."
    )

    def _detect(self) -> list[Finding]:
        """Report each `==` / `/=` with an operand bound to the ledger time."""
        flow = FieldFlow(self.index.values)
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            names = clock_names(flow, body.expr)
            if not names:
                continue
            calls = find_all(body.expr, lf.Expr.App, body.loc)
            for call in calls:
                operator = time_equality(flow, call.node, names)
                if operator is not None:
                    message = f"{body.owner}: ledger time compared with `{operator}`"
                    findings.append(self.finding(body.owner, message, call.loc))
        return findings
