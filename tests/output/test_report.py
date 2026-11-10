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
from click.testing import CliRunner

from damlisk.cli.main import cli
from damlisk.detectors.all_detectors import DETECTORS
from damlisk.output.finding import Confidence, Finding, Impact
from damlisk.output.report import DarReport, Report, cell, dar_paths, natural
from tests.conftest import BOOL_DAR, CTRL_DAR, ROOT

VULN = ROOT / "examples" / "vulnerable"


def finding(impact, message="bad"):
    return Finding("boolean-cst", impact, Confidence.HIGH, message, "pkg", "Main:T.C")


@pytest.mark.parametrize(
    "text,expected",
    [("plain", "plain"), ("a | b", "a \\| b"), ("one\ntwo", "one two")],
    ids=["plain", "pipe", "newline"],
)
def test_cell(text, expected):
    assert cell(text) == expected


@pytest.mark.parametrize(
    "names,expected",
    [
        (["a-0.1.10.dar", "a-0.1.2.dar"], ["a-0.1.2.dar", "a-0.1.10.dar"]),
        (["b-1.0.0.dar", "a-2.0.0.dar"], ["a-2.0.0.dar", "b-1.0.0.dar"]),
        (["a-v2-1.0.0.dar", "a-v1-1.0.0.dar"], ["a-v1-1.0.0.dar", "a-v2-1.0.0.dar"]),
    ],
    ids=["version", "name-first", "api-version"],
)
def test_natural(names, expected):
    paths = [VULN / name for name in names]

    assert [path.name for path in sorted(paths, key=natural)] == expected


@pytest.mark.parametrize(
    "paths,expected",
    [
        ([BOOL_DAR], ["boolean-cst.dar"]),
        ([CTRL_DAR, BOOL_DAR, BOOL_DAR], ["boolean-cst.dar", "controller-from-argument.dar"]),
        ([VULN / "boolean-cst"], ["boolean-cst.dar"]),
        ([VULN / "boolean-cst" / "daml.yaml"], []),
    ],
    ids=["file", "sorted-unique", "folder", "not-a-dar"],
)
def test_dar_paths(paths, expected):
    assert [path.name for path in dar_paths(paths)] == expected


def test_dar_paths_finds_all_examples():
    assert len(dar_paths([VULN])) == len(list(VULN.glob("*/*.dar")))


@pytest.mark.parametrize(
    "dar,expected",
    [
        (DarReport(BOOL_DAR, "p 1 (LF 2.1)", "3.4.8"), "No findings."),
        (DarReport(BOOL_DAR, error="broken archive"), "could not be loaded: broken archive"),
        (
            DarReport(BOOL_DAR, "p", "s", [finding(Impact.HIGH, "x | y")]),
            "| High | High | `boolean-cst` | `Main:T.C` | x \\| y |",
        ),
    ],
    ids=["clean", "error", "finding"],
)
def test_dar_render(dar, expected):
    page = dar.render("report-2026-11-10.md")

    assert "[Back to the summary](../report-2026-11-10.md)" in page
    assert expected in page


@pytest.mark.parametrize(
    "impact,expected",
    [(Impact.HIGH, 2), (Impact.LOW, 1), (Impact.MEDIUM, 0)],
    ids=["high", "low", "none"],
)
def test_count(impact, expected):
    found = [finding(Impact.HIGH), finding(Impact.HIGH), finding(Impact.LOW)]

    assert DarReport(BOOL_DAR, findings=found).count(impact) == expected


def test_scan_example():
    dar = DarReport.scan(BOOL_DAR, list(DETECTORS))

    assert dar.package.startswith("boolean-cst 0.0.1")
    assert len(dar.findings) == 6
    assert [item.impact.rank for item in dar.findings] == sorted(
        item.impact.rank for item in dar.findings
    )


def test_report_write(tmp_path):
    dars = [DarReport(BOOL_DAR, "p", "s", [finding(Impact.HIGH)]), DarReport(CTRL_DAR, error="x")]
    summary = Report("acme", "2026-11-10", dars).write(tmp_path)
    text = summary.read_text()

    assert summary == tmp_path / "acme" / "report-2026-11-10.md"
    assert "[boolean-cst](report-2026-11-10/boolean-cst.md) | p | 1 | 1 | 0 | 0 | 0 |" in text
    assert "| error | 0 | 0 | 0 | 0 |" in text
    assert (tmp_path / "acme" / "report-2026-11-10" / "controller-from-argument.md").exists()


@pytest.mark.parametrize(
    "args,code,expected",
    [
        (["--name", "acme", "--date", "2026-11-10", str(BOOL_DAR)], 0, "Wrote"),
        (["--name", "acme", str(VULN / "boolean-cst" / "daml.yaml")], 2, "no .dar files found"),
        (["--name", "acme", "--detect", "nope", str(BOOL_DAR)], 2, "unknown detector(s): nope"),
    ],
    ids=["writes", "no-dars", "bad-detector"],
)
def test_report_cmd(tmp_path, args, code, expected):
    result = CliRunner().invoke(cli, ["report", "--out", str(tmp_path), *args])

    assert result.exit_code == code
    assert expected in result.output
