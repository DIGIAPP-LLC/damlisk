from abc import ABC, abstractmethod
from typing import ClassVar

from dazl.damlast import daml_lf_1 as lf

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
