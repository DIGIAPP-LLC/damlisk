import pytest

from damlisk.detectors.validation.time_argument import TimeFromArgument, caller_times, reads_clock
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Claim", ["now"]),
        ("Extend", ["newUnlock"]),
        ("SafeClaim", []),
        ("BoundClaim", []),
        ("Reschedule", []),
    ],
    ids=["now-argument", "no-clock-check", "get-time", "deadline-assert", "stored-only"],
)
def test_caller_times(time_index, choice, expected):
    flow = FieldFlow(time_index.values)
    decls = {decl.choice.name: decl for decl in time_index.choices()}

    assert caller_times(time_index, flow, decls[choice]) == expected


@pytest.mark.parametrize(
    "choice,expected",
    [("Claim", False), ("SafeClaim", True), ("BoundClaim", True)],
    ids=["no-clock", "get-time", "deadline-assert"],
)
def test_reads_clock(time_index, choice, expected):
    decls = {decl.choice.name: decl for decl in time_index.choices()}

    assert reads_clock(time_index, decls[choice].choice.update) is expected


def test_detector_reports_example_violations(time_index):
    found = TimeFromArgument(time_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Vesting.Claim", 14), ("Main:Vesting.Extend", 21)]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert TimeFromArgument(index).detect() == []
