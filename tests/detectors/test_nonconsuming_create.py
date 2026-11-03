import pytest

from damlisk.detectors.validation.nonconsuming_create import (
    Creates,
    NonconsumingCreate,
    duplicates_self,
)
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Split", True),
        ("Copy", True),
        ("SafeSplit", False),
        ("SafeMove", False),
        ("Merge", False),
        ("Balance", False),
    ],
    ids=["create-this", "create-fresh", "archive-self", "exercise-archive", "consuming", "read"],
)
def test_duplicates_self(copy_index, choice, expected):
    flow = FieldFlow(copy_index.values)
    creates = Creates(copy_index)
    decls = {decl.choice.name: decl for decl in copy_index.choices()}

    assert duplicates_self(decls[choice], creates, flow) is expected


@pytest.mark.parametrize(
    "choice,expected",
    [("Split", {"Main:Token"}), ("SafeMove", {"Main:Token"}), ("Balance", set())],
    ids=["inlined", "through-helper", "none"],
)
def test_created_templates(copy_index, choice, expected):
    decls = {decl.choice.name: decl for decl in copy_index.choices()}

    assert Creates(copy_index).templates(decls[choice].choice.update) == expected


def test_detector_reports_example_violations(copy_index):
    found = NonconsumingCreate(copy_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Token.Copy", 21), ("Main:Token.Split", 12)]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert NonconsumingCreate(index).detect() == []
