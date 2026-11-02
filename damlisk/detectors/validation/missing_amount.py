from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import is_numeric
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import TemplateDecl
from damlisk.output.finding import Confidence, Finding, Impact


def ensure_condition(tmpl: lf.DefTemplate) -> lf.Expr | None:
    precond = tmpl.precond
    if precond is None:
        return None
    if precond.case is not None:
        return precond.case.scrut
    return precond


def unchecked_amounts(flow: FieldFlow, decl: TemplateDecl) -> list[str]:
    amounts = [field.field for field in decl.fields if is_numeric(field.type)]
    condition = ensure_condition(decl.template)
    if condition is None:
        return amounts
    checked = flow.fields(condition, decl.template.param)
    return [name for name in amounts if name not in checked]


class MissingAmountCheck(AbstractDetector):
    ARGUMENT = "missing-amount-check"
    HELP = "Numeric template field not constrained by ensure"
    IMPACT = Impact.LOW
    CONFIDENCE = Confidence.MEDIUM
    WIKI_TITLE = "Amount not checked by ensure"
    WIKI_DESCRIPTION = (
        "A `Decimal`/`Numeric` template field that the template's `ensure` clause never "
        "mentions: the ledger accepts contracts with zero or negative values."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "`template Iou with amount : Decimal` has no `ensure`: an issuer can create an `Iou` "
        "with `amount = -100.0`, and every choice that adds or subtracts it misbehaves."
    )
    WIKI_RECOMMENDATION = "Constrain the field in `ensure`, e.g. `ensure amount > 0.0`."

    def _detect(self) -> list[Finding]:
        flow = FieldFlow(self.index.values)
        findings = []
        decls = self.index.template_decls()
        for decl in decls:
            amounts = unchecked_amounts(flow, decl)
            if amounts:
                names = ", ".join(f"`{name}`" for name in amounts)
                message = f"{decl.owner}: ensure does not check {names}"
                findings.append(self.finding(decl.owner, message, decl.loc))
        return findings
