import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.contracts.unsafe_primitive import UnsafePrimitive, generated
from damlisk.lf.dar import Dar
from damlisk.lf.index import Body, PackageIndex
from tests.conftest import ROOT

DICT = lf.Expr(struct_con=lf.Expr.StructCon(()))
CODE = lf.Expr(var="cid")


@pytest.mark.parametrize(
    "owner,expr,expected",
    [
        ("Main:$$fHasFromAnyTemplateHolding", CODE, True),
        ("Main:$$$$sc_$$fHasFromAnyChoiceVaultPeekNumeric_1", CODE, True),
        ("Main:$$fHasFromInterfaceHoldingAsset", CODE, True),
        ("Main:Vault.Downcast.update", DICT, True),
        ("Main:Vault.Peek.update", CODE, False),
        ("Splice.Amulet.TokenApiUtils:$$cfromAnyValue2", CODE, False),
    ],
    ids=[
        "from-any-template",
        "from-any-choice-helper",
        "from-interface",
        "instance-dictionary",
        "choice",
        "user-method",
    ],
)
def test_generated(owner, expr, expected):
    assert generated(Body(owner, expr, None)) is expected


def test_detector_reports_example_violations(unsafe_index):
    found = UnsafePrimitive(unsafe_index).detect()
    rows = [(f.owner, f.line, f.message) for f in found]

    assert rows == [
        (
            "Main:Vault.Peek.update",
            23,
            "Main:Vault.Peek.update: unsafe primitive `coerceContractId`",
        ),
        (
            "Main:Vault.Unwrap.update",
            31,
            "Main:Vault.Unwrap.update: unsafe primitive `unsafeFromInterface`",
        ),
    ]


@pytest.mark.parametrize(
    "dar_name,expected",
    [
        ("splice-amulet-0.1.24.dar", 3),
        ("splice-amulet-0.1.14.dar", 3),
        ("splice-token-standard-utils-2.0.0.dar", 8),
        ("splice-wallet-payments-0.1.24.dar", 0),
        ("splice-util-0.1.8.dar", 0),
    ],
    ids=["amulet", "amulet-old", "token-utils", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name, expected):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(UnsafePrimitive(index).detect()) == expected
