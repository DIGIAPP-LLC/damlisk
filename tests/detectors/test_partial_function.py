import pytest

from damlisk.detectors.validation.partial_function import PartialFunction, describe, partial_uses
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow, PartialUse
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Payout", [PartialUse("winners", "head")]),
        ("Settle", [PartialUse("price", "fromSome")]),
        ("Latest", [PartialUse("batch", "last")]),
        ("First", []),
        ("Archive", []),
    ],
    ids=["head", "fromSome", "nonconsuming-last", "contract-state", "archive"],
)
def test_partial_uses(partial_index, choice, expected):
    flow = FieldFlow(partial_index.values)
    choices = partial_index.choices()
    decl = next(d for d in choices if d.owner == f"Main:Pool.{choice}")

    assert partial_uses(flow, decl) == expected


@pytest.mark.parametrize(
    "uses,expected",
    [
        ([PartialUse("winners", "head")], "`winners` -> head"),
        ([PartialUse("a", "head"), PartialUse("b", "last")], "`a` -> head, `b` -> last"),
        ([], ""),
    ],
    ids=["one", "two", "none"],
)
def test_describe(uses, expected):
    assert describe(uses) == expected


def test_detector_reports_example_violations(partial_index):
    found = PartialFunction(partial_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Pool.Latest", 27), ("Main:Pool.Payout", 15), ("Main:Pool.Settle", 21)]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert PartialFunction(index).detect() == []
