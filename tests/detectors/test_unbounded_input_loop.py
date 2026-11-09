import pytest

from damlisk.detectors.loops.unbounded_input_loop import UnboundedInputLoop, list_fields, unbounded
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def decl_of(index, choice):
    return next(d for d in index.choices() if d.owner == f"Main:{choice}")


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Treasury.PayAll", ["payees"]),
        ("Treasury.PayByHelper", ["payees"]),
        ("Treasury.MintAll", ["names"]),
        ("Treasury.Total", ["amounts"]),
        ("Treasury.PayCapped", []),
        ("Treasury.PayMembers", []),
    ],
    ids=["for-loop", "helper-loop", "map-loop", "pure-fold", "length-checked", "template-list"],
)
def test_unbounded(unbounded_index, choice, expected):
    flow = FieldFlow(unbounded_index.values)

    assert unbounded(unbounded_index, flow, decl_of(unbounded_index, choice)) == expected


@pytest.mark.parametrize(
    "choice,expected",
    [("Treasury.PayAll", {"payees"}), ("Treasury.PayMembers", set()), ("Cash.Pay", set())],
    ids=["list-field", "decimal-field", "party-and-decimal"],
)
def test_list_fields(unbounded_index, choice, expected):
    assert list_fields(unbounded_index, decl_of(unbounded_index, choice)) == expected


def test_detector_reports_example_violations(unbounded_index):
    found = UnboundedInputLoop(unbounded_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [
        ("Main:Treasury.MintAll", 42),
        ("Main:Treasury.PayAll", 30),
        ("Main:Treasury.PayByHelper", 36),
        ("Main:Treasury.Total", 62),
    ]


@pytest.mark.parametrize(
    "dar_name,count",
    [
        ("splice-amulet-0.1.24.dar", 10),
        ("splice-wallet-payments-0.1.24.dar", 0),
        ("splice-util-0.1.8.dar", 0),
    ],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name, count):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(UnboundedInputLoop(index).detect()) == count
