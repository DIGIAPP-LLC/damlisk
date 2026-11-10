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

from damlisk.detectors.hygiene.unused_field import (
    FieldReads,
    FieldRef,
    UnusedTemplateField,
    unused_fields,
)
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "template,expected",
    [("Shop", ["currency"]), ("Limit", []), ("Missing", [])],
    ids=["unread-field", "read-through-fetch", "unknown-template"],
)
def test_unused_fields(unused_index, template, expected):
    reads = FieldReads(unused_index).collect()
    decls = unused_index.template_decls()
    found = [unused_fields(d, reads) for d in decls if d.owner == f"Main:{template}"]

    assert (found[0] if found else []) == expected


@pytest.mark.parametrize(
    "ref,expected",
    [
        (FieldRef("Main:Shop", "note"), True),
        (FieldRef("Main:Shop", "owner"), True),
        (FieldRef("Main:Limit", "cap"), True),
        (FieldRef("Main:Shop", "currency"), False),
    ],
    ids=["returned-by-choice", "observer", "fetched-contract", "never-read"],
)
def test_field_reads(unused_index, ref, expected):
    assert (ref in FieldReads(unused_index).collect()) is expected


def test_detector_reports_example_violation(unused_index):
    found = UnusedTemplateField(unused_index).detect()
    rows = [(f.owner, f.line, f.message) for f in found]

    assert rows == [("Main:Shop", 11, "Main:Shop: no code reads `currency`")]


@pytest.mark.parametrize(
    "dar_name,owners",
    [
        (
            "splice-amulet-0.1.24.dar",
            {
                "Splice.Amulet:DevelopmentFundCoupon",
                "Splice.Amulet:RewardCouponV2",
                "Splice.Amulet:UnclaimedActivityRecord",
                "Splice.Amulet:ValidatorRight",
                "Splice.ExternalPartyConfigState:ExternalPartyConfigState",
                "Splice.Round:SummarizingMiningRound",
                "Splice.ValidatorLicense:ValidatorLicense",
            },
        ),
        (
            "splice-wallet-payments-0.1.24.dar",
            {
                "Splice.Wallet.Payment:TerminatedAppPayment",
                "Splice.Wallet.Subscriptions:TerminatedSubscription",
            },
        ),
        ("splice-api-token-holding-v1-1.0.0.dar", set()),
    ],
    ids=["amulet", "wallet-payments", "token-holding"],
)
def test_detector_on_splice(dar_name, owners):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))
    found = UnusedTemplateField(index).detect()

    assert {f.owner for f in found} == owners
