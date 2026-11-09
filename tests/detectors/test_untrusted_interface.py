import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.contracts.untrusted_interface import (
    UntrustedInterface,
    concrete_fields,
    only_templates,
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
        ("Desk.PayCash", {"cashCid", "receiver"}),
        ("Desk.SendCash", {"cashCid", "receiver"}),
        ("Desk.Settle", {"receiver"}),
        ("Desk.SettleAll", {"receiver"}),
    ],
    ids=["template-id", "cast-template-id", "interface-id", "interface-list"],
)
def test_concrete_fields(iface_index, choice, expected):
    assert concrete_fields(iface_index, decl_of(iface_index, choice)) == expected


def by_name(names, name):
    return next(tycon for tycon in names if str(tycon).endswith(f":{name}"))


def cid_of(tycon):
    con = lf.Type(con=lf.Type.Con(tycon, ()))
    return lf.Type(prim=lf.Type.Prim(lf.PrimType.CONTRACT_ID, (con,)))


def list_of(typ):
    return lf.Type(prim=lf.Type.Prim(lf.PrimType.LIST, (typ,)))


@pytest.mark.parametrize(
    "kind,expected",
    [
        ("template", True),
        ("template-list", True),
        ("interface", False),
        ("interface-list", False),
        ("text", True),
    ],
    ids=["template", "template-list", "interface", "interface-list", "no-contract-id"],
)
def test_only_templates(iface_index, kind, expected):
    cash = cid_of(by_name(iface_index.templates, "Cash"))
    holding = cid_of(by_name(iface_index.ifaces, "Holding"))
    types = {
        "template": cash,
        "template-list": list_of(cash),
        "interface": holding,
        "interface-list": list_of(holding),
        "text": lf.Type(prim=lf.Type.Prim(lf.PrimType.TEXT, ())),
    }

    assert only_templates(iface_index, types[kind], set()) is expected


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
