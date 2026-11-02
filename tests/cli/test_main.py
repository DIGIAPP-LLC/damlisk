import json

import pytest
from click.testing import CliRunner

from damlisk.cli.main import cli
from tests.conftest import AMULET_DAR, BOOL_DAR, CTRL_DAR


@pytest.mark.parametrize(
    "args,code,expected",
    [
        (["scan", str(BOOL_DAR)], 0, "5 finding(s)."),
        (["scan", str(BOOL_DAR), "--fail-on", "medium"], 1, "boolean-cst Main.daml:10"),
        (["scan", str(BOOL_DAR), "--fail-on", "high"], 0, "condition is always True"),
        (
            ["scan", str(BOOL_DAR), "--exclude", "boolean-cst,missing-amount-check"],
            0,
            "No findings.",
        ),
        (["scan", str(BOOL_DAR), "--detect", "nope"], 2, "unknown detector(s): nope"),
        (["scan", str(AMULET_DAR)], 0, "6 finding(s)."),
        (["scan", str(AMULET_DAR), "--exclude", "missing-amount-check"], 0, "No findings."),
        (["info", str(AMULET_DAR)], 0, "interface instances: 23"),
        (["list-detectors"], 0, "boolean-cst"),
        (["list-detectors"], 0, "boolean-equal"),
        (["scan", str(CTRL_DAR), "--fail-on", "high"], 1, "controller-from-argument"),
        ([], 0, "Usage:"),
    ],
    ids=[
        "scan",
        "fail-on-medium",
        "fail-on-high",
        "exclude",
        "unknown-detector",
        "splice-dar",
        "splice-dar-clean",
        "info",
        "list",
        "list-boolean-equal",
        "fail-on-high-controller",
        "help",
    ],
)
def test_cli(args, code, expected):
    result = CliRunner().invoke(cli, args)

    assert result.exit_code == code
    assert expected in result.output


@pytest.mark.parametrize("flag", ["--json", "--pretty-json"])
def test_scan_json(flag):
    result = CliRunner().invoke(cli, ["scan", str(BOOL_DAR), "--detect", "boolean-cst", flag])
    data = json.loads(result.output)

    assert result.exit_code == 0
    assert len(data["findings"]) == 4
    assert {f["check"] for f in data["findings"]} == {"boolean-cst"}
    assert all(len(f["fingerprint"]) == 64 for f in data["findings"])


@pytest.mark.parametrize("traceback,code", [(False, 2), (True, 1)])
def test_scan_reports_bad_dar(tmp_path, traceback, code):
    bad = tmp_path / "bad.dar"
    bad.write_bytes(b"not a zip")
    args = ["scan", str(bad), *(["--traceback"] if traceback else [])]

    assert CliRunner().invoke(cli, args).exit_code == code
