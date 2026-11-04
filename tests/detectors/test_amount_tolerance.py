import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.validation.amount_tolerance import AmountTolerance, tolerance
from damlisk.lf.builtins import numeric_lit
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from damlisk.lf.tree import find_all
from tests.conftest import ROOT
from tests.lf.test_flow import app, helper, val, var

LIMIT = lf.Expr(prim_lit=lf.PrimLit(numeric="0.0100000000"))
VALUES = dict(
    [helper("atMost", app(lf.Expr(builtin="GREATER_EQ"), LIMIT)), helper("same", val("x"))]
)


def _limits(index: PackageIndex, owner: str) -> list[str]:
    flow = FieldFlow(index.values)
    found = []
    bodies = index.bodies()
    for body in bodies:
        if body.owner != owner:
            continue
        calls = find_all(body.expr, lf.Expr.App)
        for call in calls:
            limit = tolerance(flow, call.node)
            if limit is not None:
                found.append(limit)
    return found


@pytest.mark.parametrize(
    "owner,expected",
    [
        ("Main:Token.Split.update", ["0.0001"]),
        ("Main:Token.Merge.update", ["0.01"]),
        ("Main:Token.SafeSplit.update", []),
        ("Main:Token.Grow.update", []),
    ],
    ids=["abs-less", "literal-first", "exact", "abs-greater-zero"],
)
def test_tolerance(eps_index, owner, expected):
    assert _limits(eps_index, owner) == expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (val("atMost"), ["0.01", None]),
        (val("same"), [None]),
        (val("missing"), [None]),
        (lf.Expr(builtin="LESS"), [None]),
    ],
    ids=["partial-helper", "alias-helper", "unknown-val", "builtin"],
)
def test_call_args(fun, expected):
    call = lf.Expr.App(fun, (var("d"),))

    args = FieldFlow(VALUES).call_args(call)

    assert [numeric_lit(arg) for arg in args] == expected


def test_detector_reports_example_violations(eps_index):
    found = AmountTolerance(eps_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Token.Merge.update", 19), ("Main:Token.Split.update", 11)]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert AmountTolerance(index).detect() == []
