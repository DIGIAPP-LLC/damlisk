from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import partial_name
from damlisk.lf.tree import all_terms, find_all, used_later
from damlisk.output.finding import Confidence, Finding, Impact


def is_optional(typ: lf.Type) -> bool:
    """Return True if `typ` is `Optional a`."""
    return typ.prim is not None and typ.prim.prim == lf.PrimType.OPTIONAL


def forced(root: lf.Expr, name: str) -> bool:
    """Return True if `fromSome` is applied directly to the variable `name` inside `root`."""
    apps = find_all(root, lf.Expr.App)
    for app in apps:
        if partial_name(app.node.fun) != "fromSome":
            continue
        for arg in app.node.args:
            if arg.var == name:
                return True
    return False


def ignored(block: lf.Block) -> list[str]:
    """Return a message for each `Optional` binding of `block` that is unused or forced."""
    found = []
    for pos, binding in enumerate(block.bindings):
        var = binding.binder.var
        if not is_optional(binding.binder.type):
            continue
        if not used_later(block, pos, var):
            found.append(f"`{var}` is never used")
            continue
        later = [item.bound for item in block.bindings[pos + 1 :]]
        later.append(block.body)
        for expr in later:
            if forced(expr, var):
                found.append(f"`{var}` is forced with fromSome")
                break
    return found


class IgnoredOptional(AbstractDetector):
    ARGUMENT = "ignored-optional"
    HELP = "Optional result discarded or forced with fromSome"
    IMPACT = Impact.MEDIUM
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Ignored optional result"
    WIKI_DESCRIPTION = (
        "A `do` block binds an `Optional` result (e.g. `r <- lookupByKey @T k` or an exercise "
        "returning `Optional`) and either never uses it or forces it with `fromSome`. The "
        "`None` case is silently ignored or aborts the transaction with a generic error."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`r <- lookupByKey @Allowance k; create Transfer with ...`: the lookup was meant as a "
        "check, but `r` is never inspected, so the transfer goes through without an allowance."
    )
    WIKI_RECOMMENDATION = (
        'Match on the result (`case r of None -> abort "..."; Some x -> ...`), or use '
        "`fromSomeNote` / `fromOptional` so the `None` case is handled on purpose."
    )

    def _detect(self) -> list[Finding]:
        """Report each body with an `Optional` binding that is never used or forced."""
        findings = []
        bodies = self.index.bodies()
        for body in bodies:
            terms = all_terms(body.expr, body.loc)
            for term in terms:
                node = term.node
                if not isinstance(node, lf.Update) or node.block is None:
                    continue
                issues = ignored(node.block)
                if issues:
                    message = f"{body.owner}: {'; '.join(issues)}"
                    findings.append(self.finding(body.owner, message, term.loc))
        return findings
