from pathlib import Path

import pytest

from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex

ROOT = Path(__file__).parent.parent
SPLICE_DARS = sorted((ROOT / "examples" / "dars").glob("*.dar"))
AMULET_DAR = ROOT / "examples" / "dars" / "splice-amulet-0.1.24.dar"
BOOL_DAR = ROOT / "examples" / "vulnerable" / "boolean-cst" / "boolean-cst.dar"
EQ_DAR = ROOT / "examples" / "vulnerable" / "boolean-equal" / "boolean-equal.dar"
AMOUNT_DAR = ROOT / "examples" / "vulnerable" / "missing-amount-check" / "missing-amount-check.dar"
CTRL_DAR = (
    ROOT / "examples" / "vulnerable" / "controller-from-argument" / "controller-from-argument.dar"
)


@pytest.fixture(scope="session")
def amulet_index() -> PackageIndex:
    return PackageIndex(Dar.load(AMULET_DAR))


@pytest.fixture(scope="session")
def bool_index() -> PackageIndex:
    return PackageIndex(Dar.load(BOOL_DAR))


@pytest.fixture(scope="session")
def eq_index() -> PackageIndex:
    return PackageIndex(Dar.load(EQ_DAR))


@pytest.fixture(scope="session")
def ctrl_index() -> PackageIndex:
    return PackageIndex(Dar.load(CTRL_DAR))


@pytest.fixture(scope="session")
def amount_index() -> PackageIndex:
    return PackageIndex(Dar.load(AMOUNT_DAR))
