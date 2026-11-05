import pytest

from damlisk.detectors.hygiene.debug_trace import DebugTrace
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def test_detector_reports_example_violations(trace_index):
    found = DebugTrace(trace_index).detect()
    rows = [(f.owner, f.line, f.message.rsplit(" ", 1)[-1]) for f in found]

    assert rows == [
        ("Main:Account.Close.update", 26, "`debugRaw`"),
        ("Main:Account.Deposit.update", 18, "`trace`"),
        ("Main:Account.Report.update", 32, "`traceId`"),
        ("Main:Account.Withdraw.update", 10, "`debug`"),
        ("Main:fee", 41, "`traceRaw`"),
    ]


@pytest.mark.parametrize(
    "dar_name,expected",
    [
        ("splice-amulet-0.1.14.dar", 3),
        ("splice-amulet-0.1.24.dar", 0),
        ("splice-wallet-payments-0.1.24.dar", 0),
        ("splice-util-0.1.8.dar", 0),
    ],
    ids=["amulet-old", "amulet", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name, expected):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))
    found = DebugTrace(index).detect()

    assert len(found) == expected
    assert all(f.owner == "Splice.AmuletRules:summarizeTransfer" for f in found)
