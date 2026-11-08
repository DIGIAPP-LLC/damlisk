import pytest

from damlisk.detectors.assets.arbitrary_party import ArbitraryParty, granted
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def decl_of(index, choice):
    return next(d for d in index.choices() if d.owner == f"Main:{choice}")


@pytest.mark.parametrize(
    "choice,signers,expected",
    [
        ("Asset.Transfer", {"issuer"}, ["newOwner"]),
        ("Asset.Seize", {"issuer"}, ["target"]),
        ("Asset.Spread", {"issuer"}, ["takers"]),
        ("Factory.AgentMint", {"issuer"}, ["receiver"]),
        ("Asset.OwnerMove", {"issuer"}, []),
        ("Asset.IssuerMove", {"issuer"}, []),
        ("Asset.CheckedMove", {"issuer"}, []),
        ("Asset.CheckedCaller", {"issuer"}, []),
        ("Asset.Claim", {"issuer"}, []),
        ("Asset.SetMemo", {"issuer"}, []),
        ("Asset.CopyOwner", {"issuer"}, []),
        ("Asset.Reissue", {"issuer"}, []),
        ("Factory.Mint", {"issuer"}, []),
        ("Factory.NoteFor", {"issuer"}, []),
        ("Factory.PaidMint", {"issuer"}, []),
    ],
    ids=[
        "argument-controller",
        "non-signatory-controller",
        "list-callback",
        "agent-mint",
        "owner-controller",
        "signatory-controller",
        "new-owner-compared",
        "controller-compared",
        "controller-is-new-owner",
        "other-field",
        "owner-from-fetch",
        "owner-from-contract",
        "signatory-mint",
        "not-an-asset",
        "controller-pays",
    ],
)
def test_granted(arbitrary_index, choice, signers, expected):
    flow = FieldFlow(arbitrary_index.values)
    items = granted(arbitrary_index, flow, decl_of(arbitrary_index, choice), signers)

    assert [item.source for item in items] == expected


def test_detector_reports_example_violations(arbitrary_index):
    found = ArbitraryParty(arbitrary_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [
        ("Main:Asset.Seize", 24),
        ("Main:Asset.Spread", 30),
        ("Main:Asset.Transfer", 17),
        ("Main:Factory.AgentMint", 104),
    ]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-amulet-0.1.14.dar", "splice-wallet-payments-0.1.24.dar"],
    ids=["amulet", "amulet-old", "wallet-payments"],
)
def test_detector_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert ArbitraryParty(index).detect() == []
