import pytest

from damlisk.detectors.validation.unconsumed_input import (
    UnconsumedInput,
    own_inputs,
    unconsumed_inputs,
)
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Merge", ["other"]),
        ("MergeAll", ["others"]),
        ("SafeMerge", []),
        ("SafeMergeAll", []),
        ("Rebase", []),
        ("Archive", []),
    ],
    ids=["single", "list", "archived", "archived-in-loop", "exercised", "no-inputs"],
)
def test_unconsumed_inputs(input_index, choice, expected):
    flow = FieldFlow(input_index.values)
    decls = {decl.choice.name: decl for decl in input_index.choices()}

    assert unconsumed_inputs(input_index, flow, decls[choice]) == expected


@pytest.mark.parametrize(
    "choice,expected",
    [("Merge", {"other"}), ("MergeAll", {"others"}), ("Archive", set())],
    ids=["cid", "cid-list", "unit-argument"],
)
def test_own_inputs(input_index, choice, expected):
    decls = {decl.choice.name: decl for decl in input_index.choices()}

    assert own_inputs(input_index, decls[choice]) == expected


def test_detector_reports_example_violations(input_index):
    found = UnconsumedInput(input_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Token.Merge", 12), ("Main:Token.MergeAll", 21)]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert UnconsumedInput(index).detect() == []
