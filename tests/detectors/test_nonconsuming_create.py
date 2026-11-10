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

from damlisk.detectors.validation.nonconsuming_create import NonconsumingCreate, duplicates_self
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("Split", True),
        ("Copy", True),
        ("SafeSplit", False),
        ("SafeMove", False),
        ("Merge", False),
        ("Balance", False),
    ],
    ids=["create-this", "create-fresh", "archive-self", "exercise-archive", "consuming", "read"],
)
def test_duplicates_self(copy_index, choice, expected):
    flow = FieldFlow(copy_index.values)
    decls = {decl.choice.name: decl for decl in copy_index.choices()}

    assert duplicates_self(decls[choice], copy_index, flow) is expected


@pytest.mark.parametrize(
    "choice,expected",
    [("Split", {"Main:Token"}), ("SafeMove", {"Main:Token"}), ("Balance", set())],
    ids=["inlined", "through-helper", "none"],
)
def test_created_templates(copy_index, choice, expected):
    decls = {decl.choice.name: decl for decl in copy_index.choices()}

    assert copy_index.created_templates(decls[choice].choice.update) == expected


def test_detector_reports_example_violations(copy_index):
    found = NonconsumingCreate(copy_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Token.Copy", 21), ("Main:Token.Split", 12)]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert NonconsumingCreate(index).detect() == []
