import pytest

from damlisk.detectors.validation.missing_ensure import (
    MissingEnsure,
    guarded_fields,
    trivial_ensure,
)
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def _decl(index, name):
    return next(d for d in index.template_decls() if d.owner == f"Main:{name}")


@pytest.mark.parametrize(
    "name,fields,trivial",
    [
        ("Holding", ["amount"], True),
        ("Lock", ["unlockAt"], True),
        ("Counter", ["count"], True),
        ("SafeHolding", ["amount"], False),
        ("Note", [], True),
    ],
    ids=["no-ensure-decimal", "ensure-true-time", "no-ensure-int", "real-ensure", "text-only"],
)
def test_template_checks(ensure_index, name, fields, trivial):
    decl = _decl(ensure_index, name)

    assert guarded_fields(decl) == fields
    assert trivial_ensure(FieldFlow(ensure_index.values), decl) is trivial


def test_detector_reports_example_violations(ensure_index):
    found = MissingEnsure(ensure_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Counter", 18), ("Main:Holding", 3), ("Main:Lock", 10)]


@pytest.mark.parametrize(
    "dar_name,expected",
    [
        ("splice-amulet-0.1.24.dar", 6),
        ("splice-amulet-0.1.14.dar", 3),
        ("splice-wallet-payments-0.1.24.dar", 0),
        ("splice-util-0.1.8.dar", 0),
    ],
    ids=["amulet", "amulet-old", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name, expected):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(MissingEnsure(index).detect()) == expected
