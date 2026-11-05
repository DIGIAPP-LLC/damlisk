from dataclasses import replace

import pytest

from damlisk.detectors.upgrade.sdk_version import SdkVersion, lf1_target
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT

UTIL = ROOT / "examples" / "dars" / "splice-util-0.1.8.dar"


def retarget(lf_ver, sdk):
    dar = Dar.load(UTIL)
    return replace(dar, sdk=sdk, main=replace(dar.main, lf_ver=lf_ver))


@pytest.mark.parametrize(
    "lf_ver,expected",
    [("1.15", True), ("1.17", True), ("2.1", False), ("2.dev", False)],
    ids=["lf-1.15", "lf-1.17", "lf-2.1", "lf-2.dev"],
)
def test_lf1_target(lf_ver, expected):
    assert lf1_target(replace(Dar.load(UTIL).main, lf_ver=lf_ver)) is expected


@pytest.mark.parametrize(
    "lf_ver,sdk,expected",
    [
        ("1.15", "2.9.4", ["splice-util: built for Daml-LF 1.15 (SDK 2.9.4)"]),
        ("1.17", None, ["splice-util: built for Daml-LF 1.17 (SDK unknown)"]),
        ("2.1", "3.5.2", []),
    ],
    ids=["lf1", "lf1-no-sdk", "lf2"],
)
def test_detector_reports_lf1_target(lf_ver, sdk, expected):
    found = SdkVersion(PackageIndex(retarget(lf_ver, sdk))).detect()

    assert [f.message for f in found] == expected


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-amulet-0.1.14.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "amulet-old", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert SdkVersion(index).detect() == []
