import pytest

from damlisk.detectors.contracts.untrusted_interface import (
    UntrustedInterface,
    template_cids,
    untrusted_cids,
)
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def decl_of(index, choice):
    return next(d for d in index.choices() if d.owner == f"Main:{choice}")


@pytest.mark.parametrize(
    "choice,signers,concrete,expected",
    [
        ("Desk.Settle", {"bank"}, set(), ["holdingCid"]),
        ("Desk.SettleAll", {"bank"}, set(), ["cids"]),
        ("Desk.Inspect", {"bank"}, set(), ["holdingCid"]),
        ("Pool.Drain", {"bank", "trader"}, set(), ["holdingCid"]),
        ("Desk.Settle", {"bank"}, {"holdingCid"}, []),
        ("Desk.SettleStored", {"bank"}, set(), []),
        ("Desk.PayCash", {"bank"}, set(), []),
        ("Desk.BankSettle", {"bank"}, set(), []),
        ("Vault.Sweep", {"keeper"}, set(), []),
        ("Holding.Send", set(), set(), []),
    ],
    ids=[
        "exercise",
        "list-callback",
        "fetch",
        "co-signatory-at-risk",
        "concrete-skipped",
        "stored-cid",
        "template-exercise",
        "controller-sole-signatory",
        "own-vault",
        "interface-choice",
    ],
)
def test_untrusted_cids(iface_index, choice, signers, concrete, expected):
    flow = FieldFlow(iface_index.values)

    assert untrusted_cids(flow, decl_of(iface_index, choice), signers, concrete) == expected


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Desk.PayCash", {"cashCid"}),
        ("Desk.SendCash", {"cashCid"}),
        ("Desk.Settle", set()),
        ("Desk.SettleAll", set()),
    ],
    ids=["template-id", "cast-template-id", "interface-id", "interface-list"],
)
def test_template_cids(iface_index, choice, expected):
    assert template_cids(iface_index, decl_of(iface_index, choice)) == expected


def test_detector_reports_example_violations(iface_index):
    found = UntrustedInterface(iface_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [
        ("Main:Desk.Inspect", 62),
        ("Main:Desk.Settle", 48),
        ("Main:Desk.SettleAll", 55),
        ("Main:Pool.Drain", 106),
    ]


@pytest.mark.parametrize(
    "dar_name",
    [
        "splice-amulet-0.1.24.dar",
        "splice-amulet-0.1.14.dar",
        "splice-api-token-transfer-instruction-v1-1.0.0.dar",
        "splice-wallet-payments-0.1.24.dar",
    ],
    ids=["amulet", "amulet-old", "transfer-instruction", "wallet-payments"],
)
def test_detector_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert UntrustedInterface(index).detect() == []
