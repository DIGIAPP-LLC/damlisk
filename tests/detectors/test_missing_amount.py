# Copyright 2026 DIGIAPP LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
