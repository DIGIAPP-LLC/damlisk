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

from damlisk.detectors.authorization.over_disclosure import OverDisclosure, arg_observers
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Settle", ["watchers"]),
        ("Report", ["reader"]),
        ("Audit", []),
        ("Peek", []),
        ("Archive", []),
    ],
    ids=["arg-list", "arg-and-field", "contract-field", "no-observers", "archive"],
)
def test_arg_observers(disclose_index, choice, expected):
    flow = FieldFlow(disclose_index.values)
    decl = next(d for d in disclose_index.choices() if d.owner == f"Main:Trade.{choice}")

    assert arg_observers(flow, decl) == expected


def test_detector_reports_example_violations(disclose_index):
    found = OverDisclosure(disclose_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Trade.Report", 19), ("Main:Trade.Settle", 12)]


@pytest.mark.parametrize(
    "dar_name,expected",
    [
        ("splice-amulet-0.1.24.dar", 7),
        ("splice-amulet-0.1.14.dar", 0),
        ("splice-api-featured-app-v2-1.0.0.dar", 1),
        ("splice-api-token-allocation-v2-1.0.0.dar", 0),
        ("splice-wallet-payments-0.1.24.dar", 0),
    ],
    ids=["amulet", "amulet-old", "featured-app", "allocation-iface-method", "wallet-payments"],
)
def test_detector_on_splice(dar_name, expected):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(OverDisclosure(index).detect()) == expected
