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

from damlisk.detectors.authorization.unprotected_archive import UnprotectedArchive, outside_ctrl
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Cancel", ["auditor"]),
        ("Burn", ["owner"]),
        ("Revoke", []),
        ("Redeem", []),
        ("Inspect", []),
        ("Archive", []),
    ],
    ids=["observer", "owner-observer", "signatory", "co-controller", "nonconsuming", "archive"],
)
def test_outside_ctrl(archive_index, choice, expected):
    flow = FieldFlow(archive_index.values)
    decl = next(d for d in archive_index.choices() if d.owner == f"Main:Asset.{choice}")

    assert outside_ctrl(flow, decl, {"issuer"}) == expected


def test_detector_reports_example_violations(archive_index):
    found = UnprotectedArchive(archive_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Asset.Burn", 16), ("Main:Asset.Cancel", 12)]


@pytest.mark.parametrize(
    "dar_name,expected",
    [
        ("splice-amulet-0.1.24.dar", 12),
        ("splice-amulet-0.1.14.dar", 10),
        ("splice-wallet-payments-0.1.24.dar", 0),
        ("splice-util-0.1.8.dar", 0),
    ],
    ids=["amulet", "amulet-old", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name, expected):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(UnprotectedArchive(index).detect()) == expected
