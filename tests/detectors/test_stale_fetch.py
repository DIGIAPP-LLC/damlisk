import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.contracts.stale_fetch import (
    Stale,
    StaleFetch,
    StaleScan,
    cid_key,
    returns_cid,
)
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from damlisk.lf.tree import find_all
from tests.conftest import ROOT

REF = lf.ModuleRef(lf.PackageRef("pkg"), lf.DottedName(("Main",)))
ACCOUNT = lf.TypeConName(REF, ("Account",))
OTHER = lf.TypeConName(REF, ("Other",))


def cid_of(tycon):
    inner = lf.Type(con=lf.Type.Con(tycon, ()))
    return lf.Type(prim=lf.Type.Prim(lf.PrimType.CONTRACT_ID, (inner,)))


def prim(kind, *args):
    return lf.Type(prim=lf.Type.Prim(kind, args))


def decl_of(index, choice):
    return next(d for d in index.choices() if d.owner == f"Main:{choice}")


@pytest.mark.parametrize(
    "expr,expected",
    [
        (lf.Expr(var="cid"), "cid"),
        (lf.Expr(rec_proj=lf.Expr.RecProj(None, "cashCid", lf.Expr(var="this"))), "this.cashCid"),
        (lf.Expr(prim_lit=lf.PrimLit(text="x")), None),
    ],
    ids=["var", "projection", "literal"],
)
def test_cid_key(expr, expected):
    assert cid_key(expr) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (cid_of(ACCOUNT), True),
        (prim(lf.PrimType.LIST, cid_of(ACCOUNT)), True),
        (prim(lf.PrimType.OPTIONAL, cid_of(ACCOUNT)), True),
        (cid_of(OTHER), False),
        (prim(lf.PrimType.UNIT), False),
    ],
    ids=["cid", "list", "optional", "other-template", "unit"],
)
def test_returns_cid(typ, expected):
    assert returns_cid(typ, ACCOUNT) is expected


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Desk.PayOut", [Stale("acc", "Withdraw")]),
        ("Desk.PayTwice", [Stale("acc", "Withdraw")]),
        ("Desk.Merge", []),
        ("Desk.Refresh", []),
        ("Desk.ReadFirst", []),
        ("Desk.Look", []),
    ],
    ids=[
        "used-after-successor",
        "used-in-next-exercise",
        "archive-merge",
        "fetch-successor",
        "computed-before",
        "nonconsuming",
    ],
)
def test_stale(stale_index, choice, expected):
    scan = StaleScan(stale_index)
    found = []
    bodies = stale_index.reachable(decl_of(stale_index, choice).choice.update)
    for body in bodies:
        for block in find_all(body, lf.Block):
            found.extend(scan.stale(block.node))

    assert found == expected


def test_detector_reports_example_violations(stale_index):
    found = StaleFetch(stale_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Desk.PayOut", 29), ("Main:Desk.PayTwice", 38)]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert StaleFetch(index).detect() == []
