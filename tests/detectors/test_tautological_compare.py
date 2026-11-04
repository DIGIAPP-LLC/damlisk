import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.hygiene.tautological_compare import (
    TautologicalCompare,
    same_value,
    self_compare,
)
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT
from tests.lf.test_flow import helper, proj, val, var

EQUAL = lf.Expr(builtin="EQUAL")
LESS = lf.Expr(builtin="LESS")
ADD = lf.Expr(builtin="ADD_NUMERIC")
ONE = lf.Expr(prim_lit=lf.PrimLit(int64=1))
FLOW = FieldFlow(dict([helper("eq", EQUAL)]))


@pytest.mark.parametrize(
    "left,right,expected",
    [
        (var("x"), var("x"), True),
        (var("x"), var("y"), False),
        (proj("this", "price"), proj("this", "price"), True),
        (proj("this", "price"), proj("this", "amount"), False),
        (proj("this", "price"), proj("arg", "price"), False),
        (ONE, ONE, False),
    ],
    ids=["same-var", "other-var", "same-field", "other-field", "other-record", "literal"],
)
def test_same_value(left, right, expected):
    assert same_value(left, right) is expected


@pytest.mark.parametrize(
    "fun,args,expected",
    [
        (EQUAL, (var("x"), var("x")), "=="),
        (LESS, (var("x"), var("x")), "<"),
        (val("eq"), (var("x"), var("x")), "=="),
        (EQUAL, (var("x"), var("y")), None),
        (ADD, (var("x"), var("x")), None),
        (EQUAL, (var("x"),), None),
    ],
    ids=["equal", "less", "alias-helper", "different", "not-a-compare", "partial"],
)
def test_self_compare(fun, args, expected):
    call = lf.Expr.App(fun, args)

    assert self_compare(FLOW, call) == expected


def test_detector_reports_example_violations(same_index):
    found = TautologicalCompare(same_index).detect()
    rows = [(f.owner, f.line, f.message.split(": ", 1)[1]) for f in found]

    assert rows == [
        ("Main:Swap.Reprice.update", 22, "value compared with itself by `/=`, always False"),
        ("Main:Swap.Settle.update", 14, "value compared with itself by `==`, always True"),
        ("Main:Swap.precond", 12, "value compared with itself by `>=`, always True"),
    ]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert TautologicalCompare(index).detect() == []
