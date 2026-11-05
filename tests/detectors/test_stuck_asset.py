import pytest

from damlisk.detectors.assets.stuck_asset import StuckAsset, holder_fields, stuck
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def template(index, name):
    return next(t for t in index.template_decls() if t.owner == f"Main:{name}")


@pytest.mark.parametrize(
    "name,expected",
    [("Holding", {"owner"}), ("Badge", {"holder"}), ("Note", set())],
    ids=["owner", "holder", "none"],
)
def test_holder_fields(stuck_index, name, expected):
    assert holder_fields(template(stuck_index, name)) == expected


@pytest.mark.parametrize(
    "name,expected",
    [("Holding", ["owner"]), ("Badge", ["holder"]), ("Token", []), ("Voucher", []), ("Note", [])],
    ids=["issuer-only", "nonconsuming-only", "owner-transfer", "co-controller", "no-holder"],
)
def test_stuck(stuck_index, name, expected):
    flow = FieldFlow(stuck_index.values)
    owner = f"Main:{name}"
    choices = [d for d in stuck_index.choices() if d.parent == owner]

    assert stuck(flow, template(stuck_index, name), choices) == expected


def test_detector_reports_example_violations(stuck_index):
    found = StuckAsset(stuck_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Badge", 15), ("Main:Holding", 3)]


@pytest.mark.parametrize(
    "dar_name,expected",
    [
        ("splice-amulet-0.1.24.dar", ["Splice.Amulet:Amulet"]),
        ("splice-amulet-0.1.14.dar", ["Splice.Amulet:Amulet"]),
        ("splice-wallet-payments-0.1.24.dar", []),
        ("splice-util-0.1.8.dar", []),
    ],
    ids=["amulet", "amulet-old", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name, expected):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert [f.owner for f in StuckAsset(index).detect()] == expected
