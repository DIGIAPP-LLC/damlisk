import pytest

from damlisk.detectors.authorization.controller_arg import ControllerFromArgument, unchecked_fields
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import SPLICE_DARS


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Transfer", ["requester"]),
        ("Approve", ["request"]),
        ("Split", []),
        ("Peek", []),
        ("Claim", []),
        ("Give", []),
        ("Burn", []),
        ("Archive", []),
    ],
    ids=[
        "argument-controller",
        "nested-argument",
        "co-controller",
        "nonconsuming",
        "checked",
        "contract-party",
        "signatories",
        "archive",
    ],
)
def test_unchecked_fields(ctrl_index, choice, expected):
    flow = FieldFlow(ctrl_index.values)
    decl = next(d for d in ctrl_index.choices() if d.owner == f"Main:Asset.{choice}")

    assert unchecked_fields(flow, decl) == expected


def test_detector_reports_example_violations(ctrl_index):
    found = [(f.owner, f.line, f.impact.value) for f in ControllerFromArgument(ctrl_index).detect()]

    assert found == [("Main:Asset.Approve", 30, "High"), ("Main:Asset.Transfer", 16, "High")]


@pytest.mark.parametrize("dar_path", SPLICE_DARS, ids=[p.stem for p in SPLICE_DARS])
def test_detector_is_silent_on_splice(dar_path):
    assert ControllerFromArgument(PackageIndex(Dar.load(dar_path))).detect() == []
