import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.hygiene.discarded_update import DiscardedUpdate, discarded_count
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT

UNIT = lf.Type(prim=lf.Type.Prim(lf.PrimType.UNIT, ()))
ACTIONS = lf.Type(
    prim=lf.Type.Prim(lf.PrimType.LIST, (lf.Type(prim=lf.Type.Prim(lf.PrimType.UPDATE, (UNIT,))),))
)
INT = lf.Type(prim=lf.Type.Prim(lf.PrimType.INT64, ()))
VALUE = lf.Expr(var="cids")
DONE = lf.Expr(prim_con=lf.PrimCon.CON_UNIT)


def _pure(typ):
    return lf.Expr(update=lf.Update(pure=lf.Pure(typ, VALUE)))


def _block(binder, bound, body):
    return lf.Block([lf.Binding(lf.VarWithType(binder, None), bound)], body)


@pytest.mark.parametrize(
    "block,expected",
    [
        (_block("ds", _pure(ACTIONS), DONE), 1),
        (_block("acts", _pure(ACTIONS), lf.Expr(var="acts")), 0),
        (_block("n", _pure(INT), DONE), 0),
        (_block("ds", VALUE, DONE), 0),
    ],
    ids=["dropped-actions", "actions-used", "plain-value", "not-pure"],
)
def test_discarded_count(block, expected):
    assert discarded_count(block) == expected


def test_detector_reports_example_violations(drop_index):
    found = DiscardedUpdate(drop_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Wallet.BurnAll.update", 19), ("Main:Wallet.BurnEach.update", 27)]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert DiscardedUpdate(index).detect() == []
