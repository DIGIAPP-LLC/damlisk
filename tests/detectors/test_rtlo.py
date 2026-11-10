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

from damlisk.detectors.hygiene.rtlo import Rtlo, bidi_chars, bidi_lines
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT


@pytest.mark.parametrize(
    "text,expected",
    [
        ("user‮txt.exe", ["U+202E"]),
        ("a⁦b⁩", ["U+2066", "U+2069"]),
        ("‮‮", ["U+202E"]),
        ("invoice.pdf", []),
        ("שלום", []),
    ],
    ids=["rlo", "isolate-pair", "repeated", "plain", "rtl-letters"],
)
def test_bidi_chars(text, expected):
    assert bidi_chars(text) == expected


def test_bidi_lines(rtlo_index):
    scope = next(rtlo_index.scopes(rtlo_index.dar.main))
    rows = [(loc.range.start_line + 1, loc.range.start_col) for loc in bidi_lines(scope)]

    assert rows == [(15, 39)]


def test_detector_reports_example_violations(rtlo_index):
    found = Rtlo(rtlo_index).detect()
    rows = [(f.owner, f.line, f.message) for f in found]

    assert rows == [
        ("Main", 15, "Main: bidirectional control character U+202E in source"),
        ("Main:Asset.Rename.update", 18, "Main:Asset.Rename.update: Text literal contains U+202E"),
    ]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert Rtlo(index).detect() == []
