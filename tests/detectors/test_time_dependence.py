import pytest

from damlisk.detectors.time.time_dependence import TimeDependence, time_branch
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def decl_of(index, choice):
    return next(d for d in index.choices() if d.owner == f"Main:{choice}")


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Auction.Close", True),
        ("Auction.Bid", True),
        ("Auction.Settle", True),
        ("Auction.Expire", True),
        ("Auction.Withdraw", True),
        ("Auction.Stamp", False),
        ("Auction.Reprice", False),
        ("Auction.Reschedule", False),
    ],
    ids=[
        "if-on-time",
        "assert-on-time",
        "helper-on-time",
        "deadline-helper",
        "ledger-time-lt",
        "time-stored-only",
        "no-time",
        "argument-time",
    ],
)
def test_time_branch(depend_index, choice, expected):
    flow = FieldFlow(depend_index.values, clock=True)

    assert time_branch(flow, decl_of(depend_index, choice)) is expected


def test_detector_reports_example_violations(depend_index):
    found = TimeDependence(depend_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [
        ("Main:Auction.Bid", 25),
        ("Main:Auction.Close", 19),
        ("Main:Auction.Expire", 40),
        ("Main:Auction.Settle", 34),
        ("Main:Auction.Withdraw", 44),
    ]


@pytest.mark.parametrize(
    "dar_name,count",
    [
        ("splice-amulet-0.1.24.dar", 29),
        ("splice-wallet-payments-0.1.24.dar", 5),
        ("splice-util-0.1.8.dar", 0),
    ],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name, count):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(TimeDependence(index).detect()) == count
