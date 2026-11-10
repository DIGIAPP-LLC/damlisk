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

from damlisk.detectors.time.weak_randomness import WeakRandomness, weak_picks
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


def decl_of(index, choice):
    return next(d for d in index.choices() if d.owner == f"Main:{choice}")


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Lottery.DrawByTime", ["ledger time picks a list element"]),
        ("Lottery.DrawByHash", ["a hash picks a list element"]),
        ("Lottery.DrawByHelper", ["ledger time picks a list element"]),
        ("Lottery.DrawByMap", ["ledger time picks a map entry"]),
        ("Lottery.FindByHash", []),
        ("Lottery.DrawByArg", []),
        ("Lottery.Seal", []),
        ("Lottery.Close", []),
    ],
    ids=[
        "time-index",
        "hash-index",
        "helper-index",
        "time-map-key",
        "hash-map-key",
        "argument-index",
        "hash-stored",
        "time-branch",
    ],
)
def test_weak_picks(random_index, choice, expected):
    flow = FieldFlow(random_index.values, clock=True, hashes=True)

    assert weak_picks(flow, decl_of(random_index, choice)) == expected


def test_detector_reports_example_violations(random_index):
    found = WeakRandomness(random_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [
        ("Main:Lottery.DrawByHash", 33),
        ("Main:Lottery.DrawByHelper", 41),
        ("Main:Lottery.DrawByMap", 55),
        ("Main:Lottery.DrawByTime", 25),
    ]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert WeakRandomness(index).detect() == []
