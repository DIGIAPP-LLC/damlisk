import pytest

from damlisk.detectors.validation.unchecked_fetch import UncheckedFetch, unchecked_fetches
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "choice,expected",
    [("Borrow", ["collateral"]), ("BorrowUsd", ["collateral"]), ("SafeBorrow", []), ("Exists", [])],
    ids=["unchecked", "constant-check", "checked", "not-read"],
)
def test_unchecked_fetches(fetch_index, choice, expected):
    flow = FieldFlow(fetch_index.values)
    decls = {decl.choice.name: decl for decl in fetch_index.choices()}

    assert unchecked_fetches(flow, decls[choice]) == expected


def test_detector_reports_example_violations(fetch_index):
    found = UncheckedFetch(fetch_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Bank.Borrow", 29), ("Main:Bank.BorrowUsd", 38)]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert UncheckedFetch(index).detect() == []
