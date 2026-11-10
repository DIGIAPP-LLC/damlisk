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

import zipfile

import pytest

from damlisk.exceptions import DarError
from damlisk.lf.dar import Dar, Manifest
from tests.conftest import AMULET_DAR, SPLICE_DARS


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Main-Dalf: p-1-ab/p-1-ab.dalf\nSdk-Version: 3.4.8\n", ("p-1-ab", "ab", "3.4.8")),
        ("Main-Dalf: p-cd/very\r\n long-cd.dalf\n", ("p-cd", "cd", None)),
        ("garbage\n\nName: x\n", ("", "", None)),
    ],
    ids=["plain", "continuation", "garbage"],
)
def test_manifest_parse(raw, expected):
    manifest = Manifest.parse(raw)

    assert (manifest.root, manifest.main_id, manifest.sdk) == expected


@pytest.mark.parametrize("dar_path", SPLICE_DARS, ids=[p.stem for p in SPLICE_DARS])
def test_splice_dars_load_and_force_every_value(dar_path):
    dar = Dar.load(dar_path)

    assert dar.main.lf_ver == "2.1"
    assert dar.main.name in dar_path.stem
    assert all(dv.expr is not None for p in dar.packages for m in p.modules for dv in m.values)


def test_amulet_dar_decodes_lf2_extras():
    dar = Dar.load(AMULET_DAR)

    assert (dar.main.name, dar.main.version, dar.sdk) == ("splice-amulet", "0.1.24", "3.5.2")
    assert len(dar.main.extras.implements) == 23
    assert len(dar.packages) == 51
    assert "Splice.Amulet" in dar.sources


def _zip(path, files):
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in files.items():
            zf.writestr(name, data)
    return path


@pytest.mark.parametrize(
    "files,message",
    [
        (None, "not a valid DAR"),
        ({"x.txt": "x"}, "has no META-INF/MANIFEST.MF"),
        ({"META-INF/MANIFEST.MF": "Name: x\n"}, "no Main-Dalf"),
        ({"META-INF/MANIFEST.MF": "Main-Dalf: p-abc/p-abc.dalf\n"}, "does not contain its main"),
    ],
    ids=["not-zip", "no-manifest", "no-main-dalf", "missing-main"],
)
def test_load_dar_rejects_bad_input(tmp_path, files, message):
    path = tmp_path / "bad.dar"
    if files is None:
        path.write_bytes(b"not a zip")
    else:
        _zip(path, files)

    with pytest.raises(DarError, match=message):
        Dar.load(path)
