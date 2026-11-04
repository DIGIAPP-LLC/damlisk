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
UNUSED_DAR = (
    ROOT / "examples" / "vulnerable" / "unused-template-field" / "unused-template-field.dar"
)
PARTY_DAR = ROOT / "examples" / "vulnerable" / "hardcoded-party" / "hardcoded-party.dar"
PARTIAL_DAR = ROOT / "examples" / "vulnerable" / "partial-function" / "partial-function.dar"
COPY_DAR = ROOT / "examples" / "vulnerable" / "nonconsuming-create" / "nonconsuming-create.dar"
FETCH_DAR = ROOT / "examples" / "vulnerable" / "unchecked-fetch" / "unchecked-fetch.dar"
TIME_DAR = ROOT / "examples" / "vulnerable" / "time-from-argument" / "time-from-argument.dar"
DIV_DAR = ROOT / "examples" / "vulnerable" / "divide-before-multiply" / "divide-before-multiply.dar"
HASH_DAR = ROOT / "examples" / "vulnerable" / "hash-concat-collision" / "hash-concat-collision.dar"
CLOCK_DAR = ROOT / "examples" / "vulnerable" / "time-equality" / "time-equality.dar"
ABORT_DAR = ROOT / "examples" / "vulnerable" / "aborting-choice" / "aborting-choice.dar"
INPUT_DAR = ROOT / "examples" / "vulnerable" / "unconsumed-input" / "unconsumed-input.dar"
EPS_DAR = ROOT / "examples" / "vulnerable" / "amount-tolerance" / "amount-tolerance.dar"
DROP_DAR = ROOT / "examples" / "vulnerable" / "discarded-update" / "discarded-update.dar"
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


@pytest.fixture(scope="session")
def unused_index() -> PackageIndex:
    return PackageIndex(Dar.load(UNUSED_DAR))


@pytest.fixture(scope="session")
def party_index() -> PackageIndex:
    return PackageIndex(Dar.load(PARTY_DAR))


@pytest.fixture(scope="session")
def partial_index() -> PackageIndex:
    return PackageIndex(Dar.load(PARTIAL_DAR))


@pytest.fixture(scope="session")
def drop_index() -> PackageIndex:
    return PackageIndex(Dar.load(DROP_DAR))


@pytest.fixture(scope="session")
def copy_index() -> PackageIndex:
    return PackageIndex(Dar.load(COPY_DAR))


@pytest.fixture(scope="session")
def fetch_index() -> PackageIndex:
    return PackageIndex(Dar.load(FETCH_DAR))


@pytest.fixture(scope="session")
def time_index() -> PackageIndex:
    return PackageIndex(Dar.load(TIME_DAR))


@pytest.fixture(scope="session")
def eps_index() -> PackageIndex:
    return PackageIndex(Dar.load(EPS_DAR))


@pytest.fixture(scope="session")
def div_index() -> PackageIndex:
    return PackageIndex(Dar.load(DIV_DAR))


@pytest.fixture(scope="session")
def input_index() -> PackageIndex:
    return PackageIndex(Dar.load(INPUT_DAR))


@pytest.fixture(scope="session")
def abort_index() -> PackageIndex:
    return PackageIndex(Dar.load(ABORT_DAR))


@pytest.fixture(scope="session")
def hash_index() -> PackageIndex:
    return PackageIndex(Dar.load(HASH_DAR))


@pytest.fixture(scope="session")
def clock_index() -> PackageIndex:
    return PackageIndex(Dar.load(CLOCK_DAR))
