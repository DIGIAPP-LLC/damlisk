import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.authorization.hardcoded_party import HardcodedParty, misuse, preview
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT

LF_REF = lf.ModuleRef(lf.PackageRef("pkg"), lf.DottedName(("DA", "Internal", "LF")))
FROM_TEXT = lf.Expr(val=lf.ValName(LF_REF, ("partyFromText",)))
TO_TEXT = lf.Expr(val=lf.ValName(LF_REF, ("partyToText",)))
EQUAL = lf.Expr(builtin="EQUAL")
TEXT = lf.Expr(prim_lit=lf.PrimLit(text="Alice::1220"))
VAR = lf.Expr(var="name")


def _app(fun, *args):
    return lf.Expr.App(fun, tuple(args))


def _expr(call):
    return lf.Expr(app=call)


@pytest.mark.parametrize(
    "call,expected",
    [
        (_app(FROM_TEXT, TEXT), 'party built from text literal "Alice::1220"'),
        (_app(lf.Expr(builtin="TEXT_TO_PARTY"), TEXT), "party built from text literal"),
        (_app(EQUAL, _expr(_app(TO_TEXT, VAR)), TEXT), "party compared with text literal"),
        (_app(FROM_TEXT, VAR), None),
        (_app(EQUAL, VAR, TEXT), None),
        (_app(lf.Expr(builtin="APPEND_TEXT"), _expr(_app(TO_TEXT, VAR)), TEXT), None),
    ],
    ids=[
        "from-literal",
        "from-literal-builtin",
        "compare-literal",
        "from-argument",
        "compare-plain-text",
        "format-party",
    ],
)
def test_misuse(call, expected):
    result = misuse(call)

    assert (result is None) if expected is None else expected in result


@pytest.mark.parametrize(
    "text,expected",
    [("short", '"short"'), ("x" * 24, '"' + "x" * 24 + '"'), ("y" * 30, '"' + "y" * 24 + '..."')],
    ids=["short", "limit", "long"],
)
def test_preview(text, expected):
    assert preview(text) == expected


def test_detector_reports_example_violations(party_index):
    found = HardcodedParty(party_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Vault.Withdraw.update", 21), ("Main:hidden", 10), ("Main:operator", 7)]


@pytest.mark.parametrize(
    "dar_name,owners",
    [
        (
            "splice-token-standard-utils-2.0.0.dar",
            {"Splice.TokenStandard.Utils.Internal.Conversions:specialAccountOwnerStubV1"},
        ),
        ("splice-amulet-0.1.24.dar", set()),
        ("splice-wallet-payments-0.1.24.dar", set()),
    ],
    ids=["token-standard-utils", "amulet", "wallet-payments"],
)
def test_detector_on_splice(dar_name, owners):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))
    found = HardcodedParty(index).detect()

    assert {f.owner for f in found} == owners
