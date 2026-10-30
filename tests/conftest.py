from pathlib import Path

import pytest

from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex

ROOT = Path(__file__).parent.parent
SPLICE_DARS = sorted((ROOT / "examples" / "dars").glob("*.dar"))
AMULET_DAR = ROOT / "examples" / "dars" / "splice-amulet-0.1.24.dar"
BOOL_DAR = ROOT / "examples" / "vulnerable" / "boolean-cst" / "boolean-cst.dar"


@pytest.fixture(scope="session")
def amulet_index() -> PackageIndex:
    return PackageIndex(Dar.load(AMULET_DAR))


@pytest.fixture(scope="session")
def bool_index() -> PackageIndex:
    return PackageIndex(Dar.load(BOOL_DAR))
