import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.hygiene.aborting_choice import AbortingChoice, Aborts
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT
from tests.lf.test_flow import app, do_bind, helper, lam, let, val, var

ERROR = lf.Expr(builtin="ERROR")
THROW = lf.Expr(throw=lf.Expr.Throw(None, None, var("e")))
FAIL = app(ERROR, var("msg"))
DONE = lf.Expr(update=lf.Update(pure=lf.Pure(None, var("x"))))
VALUES = dict(
    [
        helper("fail", lam(["msg"], FAIL)),
        helper("loop", app(val("loop"), var("x"))),
        helper("ok", lam(["x"], var("x"))),
    ]
)


def case(*bodies):
    alts = [lf.CaseAlt(default=lf.Unit(), body=body) for body in bodies]
    return lf.Expr(case=lf.Case(var("c"), alts))


def embed(body):
    return lf.Expr(update=lf.Update(embed_expr=lf.Update.EmbedExpr(None, body)))


@pytest.mark.parametrize(
    "expr,expected",
    [
        (FAIL, True),
        (THROW, True),
        (app(val("fail"), var("m")), True),
        (let("y", var("x"), app(val("fail"), var("m"))), True),
        (do_bind("u", app(val("fail"), var("m")), DONE), True),
        (do_bind("u", DONE, embed(FAIL)), True),
        (case(FAIL, THROW), True),
        (case(FAIL, DONE), False),
        (case(), False),
        (do_bind("u", DONE, DONE), False),
        (app(val("ok"), var("m")), False),
        (app(val("loop"), var("m")), False),
        (app(val("missing"), var("m")), False),
        (lf.Expr(builtin="ADD_INT64"), False),
    ],
    ids=[
        "error-builtin",
        "throw",
        "helper",
        "let-body",
        "do-statement",
        "embedded",
        "all-branches",
        "one-branch",
        "no-branches",
        "pure-block",
        "pure-helper",
        "recursive-helper",
        "unknown-value",
        "other-builtin",
    ],
)
def test_aborts(expr, expected):
    assert Aborts(VALUES).expr(expr) is expected


def test_detector_reports_example_violations(abort_index):
    found = AbortingChoice(abort_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Vault.Close", 18), ("Main:Vault.Withdraw", 14)]


@pytest.mark.parametrize(
    "dar_name,expected",
    [
        ("splice-amulet-0.1.24.dar", 9),
        ("splice-amulet-0.1.14.dar", 4),
        ("splice-wallet-payments-0.1.24.dar", 0),
    ],
    ids=["amulet-24", "amulet-14", "wallet-payments"],
)
def test_detector_finds_deprecated_splice_choices(dar_name, expected):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(AbortingChoice(index).detect()) == expected
