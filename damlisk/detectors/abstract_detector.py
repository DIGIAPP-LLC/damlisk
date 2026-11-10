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

from abc import ABC, abstractmethod
from typing import ClassVar

from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from damlisk.output.finding import Confidence, Finding, Impact


class AbstractDetector(ABC):
    ARGUMENT: ClassVar[str] = ""
    HELP: ClassVar[str] = ""
    IMPACT: ClassVar[Impact] = Impact.INFORMATIONAL
    CONFIDENCE: ClassVar[Confidence] = Confidence.HIGH
    WIKI_TITLE: ClassVar[str] = ""
    WIKI_DESCRIPTION: ClassVar[str] = ""
    WIKI_EXPLOIT_SCENARIO: ClassVar[str] = ""
    WIKI_RECOMMENDATION: ClassVar[str] = ""

    def __init__(self, index: PackageIndex) -> None:
        self.index = index

    @abstractmethod
    def _detect(self) -> list[Finding]: ...

    def detect(self) -> list[Finding]:
        return sorted(self._detect(), key=lambda f: (f.impact.rank, f.owner, f.line or 0))

    def signers(self, flow: FieldFlow) -> dict[str, set[str]]:
        """Return the signatory fields of every main-package template, by template owner."""
        found = {}
        tmpls = self.index.template_decls()
        for tmpl in tmpls:
            sigs = tmpl.template.signatories
            if sigs is not None:
                found[tmpl.owner] = flow.fields(sigs, tmpl.template.param)
        return found

    def finding(self, owner: str, message: str, loc: lf.Location | None) -> Finding:
        return Finding(
            check=self.ARGUMENT,
            impact=self.IMPACT,
            confidence=self.CONFIDENCE,
            message=message,
            package=self.index.dar.main.name,
            owner=owner,
            loc=loc,
        )
