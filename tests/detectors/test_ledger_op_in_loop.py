import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.loops.ledger_op_in_loop import LedgerOpInLoop, LoopScan
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def decl_of(index, choice):
    return next(d for d in index.choices() if d.owner == f"Main:{choice}")


def update(**kind):
    return lf.Expr(update=lf.Update(**kind))


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Treasury.PayAll", {"exercise"}),
        ("Treasury.MintAll", {"create"}),
        ("Treasury.MintByHelper", {"create"}),
        ("Treasury.ArchiveAll", {"exercise"}),
        ("Treasury.ReadAll", {"fetch"}),
        ("Treasury.Total", set()),
        ("Treasury.MintOne", set()),
        ("Treasury.Label", set()),
    ],
    ids=[
        "exercise-lambda",
        "create-lambda",
        "create-helper",
        "archive-callback",
        "fetch-callback",
        "pure-fold",
        "no-loop",
        "pure-map",
    ],
)
def test_looped(loop_index, choice, expected):
    scan = LoopScan(loop_index.values)

    assert scan.looped(decl_of(loop_index, choice).choice.update) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (update(create=lf.Update.Create(None, lf.Expr(var="r"))), {"create"}),
        (update(fetch=lf.Update.Fetch(None, lf.Expr(var="cid"))), {"fetch"}),
        (update(get_time=lf.Unit()), set()),
        (lf.Expr(var="x"), set()),
    ],
    ids=["create", "fetch", "get-time", "var"],
)
def test_ops(expr, expected):
    assert LoopScan({}).ops(expr) == expected


def test_detector_reports_example_violations(loop_index):
    found = LedgerOpInLoop(loop_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [
        ("Main:Treasury.ArchiveAll", 47),
        ("Main:Treasury.MintAll", 35),
        ("Main:Treasury.MintByHelper", 41),
        ("Main:Treasury.PayAll", 29),
        ("Main:Treasury.ReadAll", 53),
    ]


@pytest.mark.parametrize(
    "dar_name,count",
    [
        ("splice-amulet-0.1.24.dar", 20),
        ("splice-wallet-payments-0.1.24.dar", 0),
        ("splice-util-0.1.8.dar", 0),
    ],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name, count):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(LedgerOpInLoop(index).detect()) == count
