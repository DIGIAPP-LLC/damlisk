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
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.authorization.delegated_leak import (
    DelegatedLeak,
    LeakCheck,
    ensured,
    party_or_amount,
)
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def prim(kind, *args):
    return lf.Type(prim=lf.Type.Prim(kind, args))


def decl_of(index, choice):
    return next(d for d in index.choices() if d.owner == f"Main:{choice}")


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("IssueRight.Mint", ["value"]),
        ("IssueRight.Grant", ["payee"]),
        ("IssueRight.Forward", ["payee", "value"]),
        ("IssueRight.Request", ["value"]),
        ("IssueRight.Capped", []),
        ("IssueRight.Memo", []),
        ("IssueRight.Redeem", []),
        ("IssueRight.Book", []),
        ("IssueRight.Spend", []),
        ("IssueRight.Claim", []),
        ("IssueRight.Reissue", []),
        ("Rules.Pay", []),
    ],
    ids=[
        "create-amount",
        "create-party",
        "exercise-stored-cid",
        "controller-arg-dropped",
        "bounded-arg",
        "own-authority",
        "ensure-and-text",
        "controller-cosigns",
        "controller-passed",
        "no-arg",
        "signatory-controller",
        "rules-signatory",
    ],
)
def test_leaked(leak_index, choice, expected):
    check = LeakCheck(leak_index)

    assert check.leaked(decl_of(leak_index, choice)) == expected


@pytest.mark.parametrize(
    "created,parties,expected",
    [
        ({"Main:Ticket"}, {"holder"}, True),
        ({"Main:Token"}, {"holder"}, False),
        ({"Main:Token", "Main:Note"}, {"holder"}, True),
        (set(), {"holder"}, False),
    ],
    ids=["cosigned", "issuer-only", "one-of-many", "nothing-created"],
)
def test_cosigned(leak_index, created, parties, expected):
    assert LeakCheck(leak_index).cosigned(created, parties) is expected


@pytest.mark.parametrize(
    "choice,created,expected",
    [
        ("IssueRight.Redeem", {"Main:Voucher"}, set()),
        ("IssueRight.Mint", {"Main:Token"}, {"value"}),
        ("IssueRight.Request", set(), {"requester", "value"}),
    ],
    ids=["ensured-dropped", "amount-kept", "party-kept"],
)
def test_risky(leak_index, choice, created, expected):
    check = LeakCheck(leak_index)

    assert check.risky(decl_of(leak_index, choice), created) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (prim(lf.PrimType.PARTY), True),
        (prim(lf.PrimType.NUMERIC), True),
        (prim(lf.PrimType.INT64), True),
        (prim(lf.PrimType.LIST, prim(lf.PrimType.PARTY)), True),
        (prim(lf.PrimType.OPTIONAL, prim(lf.PrimType.NUMERIC)), True),
        (prim(lf.PrimType.TEXT), False),
        (prim(lf.PrimType.LIST, prim(lf.PrimType.TEXT)), False),
        (prim(lf.PrimType.CONTRACT_ID, prim(lf.PrimType.PARTY)), False),
    ],
    ids=["party", "numeric", "int", "party-list", "optional-amount", "text", "text-list", "cid"],
)
def test_party_or_amount(typ, expected):
    assert party_or_amount(typ) is expected


@pytest.mark.parametrize(
    "template,expected",
    [("Main:Voucher", {"value"}), ("Main:Token", set()), ("Main:Note", set())],
    ids=["ensure", "no-ensure", "no-ensure-signed"],
)
def test_ensured(leak_index, template, expected):
    flow = FieldFlow(leak_index.values)
    tmpl = next(t for t in leak_index.template_decls() if t.owner == template)

    assert ensured(flow, tmpl) == expected


def test_detector_reports_example_violations(leak_index):
    found = DelegatedLeak(leak_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [
        ("Main:IssueRight.Forward", 53),
        ("Main:IssueRight.Grant", 47),
        ("Main:IssueRight.Mint", 41),
        ("Main:IssueRight.Request", 84),
    ]


@pytest.mark.parametrize(
    "dar_name,expected",
    [
        ("splice-amulet-0.1.24.dar", 1),
        ("splice-amulet-0.1.14.dar", 0),
        ("splice-token-standard-utils-2.0.0.dar", 0),
        ("splice-wallet-payments-0.1.24.dar", 0),
    ],
    ids=["amulet", "amulet-old", "token-utils", "wallet-payments"],
)
def test_detector_on_splice(dar_name, expected):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(DelegatedLeak(index).detect()) == expected
