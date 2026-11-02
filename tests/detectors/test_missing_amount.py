import pytest

from damlisk.detectors.validation.missing_amount import MissingAmountCheck, unchecked_amounts
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "template,expected",
    [("Iou", ["amount"]), ("Order", ["price"]), ("Bond", []), ("Token", []), ("Counter", [])],
    ids=["no-ensure", "partial-ensure", "checked", "checked-by-helper", "int-only"],
)
def test_unchecked_amounts(amount_index, template, expected):
    flow = FieldFlow(amount_index.values)
    decls = amount_index.template_decls()
    decl = next(d for d in decls if d.owner == f"Main:{template}")

    assert unchecked_amounts(flow, decl) == expected


def test_detector_reports_example_violations(amount_index):
    found = MissingAmountCheck(amount_index).detect()
    rows = [(f.owner, f.line, f.impact.value) for f in found]

    assert rows == [("Main:Iou", 6, "Low"), ("Main:Order", 15, "Low")]


@pytest.mark.parametrize(
    "dar_name,owners",
    [
        (
            "splice-amulet-0.1.24.dar",
            {
                "Splice.ExternalPartyAmuletRules:TransferCommand",
                "Splice.ExternalPartyConfigState:ExternalPartyConfigState",
                "Splice.Round:ClosedMiningRound",
                "Splice.Round:IssuingMiningRound",
                "Splice.Round:OpenMiningRound",
                "Splice.Round:SummarizingMiningRound",
            },
        ),
        (
            "splice-wallet-payments-0.1.24.dar",
            {
                "Splice.Wallet.Subscriptions:SubscriptionInitialPayment",
                "Splice.Wallet.Subscriptions:SubscriptionPayment",
            },
        ),
        ("splice-api-token-holding-v1-1.0.0.dar", set()),
    ],
    ids=["amulet", "wallet-payments", "token-holding"],
)
def test_detector_on_splice(dar_name, owners):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))
    found = MissingAmountCheck(index).detect()

    assert {f.owner for f in found} == owners
