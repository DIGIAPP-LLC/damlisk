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

import re
from dataclasses import dataclass, field
from pathlib import Path

from damlisk import __version__
from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.exceptions import DamliskException
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from damlisk.output.finding import Finding, Impact


def run_detectors(index: PackageIndex, detectors: list[type[AbstractDetector]]) -> list[Finding]:
    """Run each detector over `index` and return all findings in detector order."""
    findings: list[Finding] = []
    for det in detectors:
        found = det(index).detect()
        findings.extend(found)
    return findings


def natural(path: Path) -> list[str | int]:
    """Sort key that orders numbers by value, so `x-0.1.2` comes before `x-0.1.10`."""
    parts = re.split(r"(\d+)", path.name)
    return [int(part) if part.isdigit() else part for part in parts]


def dar_paths(paths: list[Path]) -> list[Path]:
    """Return the DAR files named in `paths`, searching folders recursively, in version order."""
    found: dict[Path, None] = {}
    for path in paths:
        if path.is_dir():
            nested = sorted(path.rglob("*.dar"))
            found.update(dict.fromkeys(nested))
        elif path.suffix == ".dar":
            found[path] = None
    return sorted(found, key=natural)


def cell(text: str) -> str:
    """Make `text` safe inside a Markdown table cell."""
    return text.replace("|", "\\|").replace("\n", " ")


@dataclass
class DarReport:
    path: Path
    package: str = ""
    sdk: str = ""
    findings: list[Finding] = field(default_factory=list)
    error: str | None = None

    @property
    def name(self) -> str:
        return self.path.stem

    def count(self, impact: Impact) -> int:
        """Return how many findings have `impact`."""
        return sum(1 for item in self.findings if item.impact == impact)

    @classmethod
    def scan(cls, path: Path, detectors: list[type[AbstractDetector]]) -> "DarReport":
        """Load and scan one DAR; a DAR that cannot be loaded is kept with its error."""
        try:
            dar = Dar.load(path)
        except DamliskException as err:
            return cls(path, error=str(err))
        main = dar.main
        package = f"{main.name} {main.version} (LF {main.lf_ver})"
        findings = run_detectors(PackageIndex(dar), detectors)
        ordered = sorted(findings, key=lambda item: (item.impact.rank, item.check, item.owner))
        return cls(path, package, dar.sdk or "unknown", ordered)

    def render(self, index: str) -> str:
        """Render this DAR's findings as a Markdown page linking back to `index`."""
        lines = [
            f"# {self.name}",
            "",
            f"[Back to the summary](../{index})",
            "",
            f"- **Package:** {self.package or 'n/a'}",
            f"- **SDK:** {self.sdk or 'n/a'}",
            f"- **Findings:** {len(self.findings)}",
            "",
        ]
        if self.error:
            return "\n".join([*lines, f"The DAR could not be loaded: {self.error}", ""])
        if not self.findings:
            return "\n".join([*lines, "No findings.", ""])
        lines += [
            "| Impact | Confidence | Detector | Location | Finding |",
            "|---|---|---|---|---|",
        ]
        for item in self.findings:
            level = f"{item.impact.value} | {item.confidence.value}"
            text = cell(item.message)
            lines.append(f"| {level} | `{item.check}` | `{item.where}` | {text} |")
        return "\n".join([*lines, ""])


@dataclass
class Report:
    name: str
    date: str
    dars: list[DarReport]

    @property
    def stem(self) -> str:
        return f"report-{self.date}"

    def render(self) -> str:
        """Render the summary page: one row per DAR with counts and a link to its page."""
        total = sum(len(dar.findings) for dar in self.dars)
        heads = [impact.value for impact in Impact]
        lines = [
            f"# {self.name} report {self.date}",
            "",
            f"Scanned {len(self.dars)} DAR(s) with damlisk {__version__}: {total} finding(s).",
            "",
            f"| DAR | Package | Findings | {' | '.join(heads)} |",
            "|---|---|---|" + "---|" * len(heads),
        ]
        for dar in self.dars:
            link = f"[{dar.name}]({self.stem}/{dar.name}.md)"
            counts = " | ".join(str(dar.count(impact)) for impact in Impact)
            found = "error" if dar.error else str(len(dar.findings))
            lines.append(f"| {link} | {cell(dar.package)} | {found} | {counts} |")
        return "\n".join([*lines, ""])

    def write(self, out: Path) -> Path:
        """Write the summary and per-DAR pages under `out/<name>/`; return the summary path."""
        root = out / self.name
        pages = root / self.stem
        pages.mkdir(parents=True, exist_ok=True)
        for dar in self.dars:
            page = pages / f"{dar.name}.md"
            page.write_text(dar.render(f"{self.stem}.md"))
        summary = root / f"{self.stem}.md"
        summary.write_text(self.render())
        return summary
