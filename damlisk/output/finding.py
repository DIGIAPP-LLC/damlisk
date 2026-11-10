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

import hashlib
from dataclasses import dataclass
from enum import Enum

from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.util import module_name


class Impact(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"

    @property
    def rank(self) -> int:
        return list(Impact).index(self)


class Confidence(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


JsonValue = str | int | None


@dataclass(frozen=True)
class Finding:
    check: str
    impact: Impact
    confidence: Confidence
    message: str
    package: str
    owner: str
    loc: lf.Location | None = None

    @property
    def file(self) -> str | None:
        return "/".join(module_name(self.loc.module).segments) + ".daml" if self.loc else None

    @property
    def line(self) -> int | None:
        return self.loc.range.start_line + 1 if self.loc else None

    @property
    def where(self) -> str:
        return f"{self.file}:{self.line}" if self.loc else self.owner

    @property
    def fingerprint(self) -> str:
        raw = "|".join((self.check, self.package, self.owner, self.message))
        return hashlib.sha256(raw.encode()).hexdigest()

    def to_json(self) -> dict[str, JsonValue]:
        return {
            "check": self.check,
            "impact": self.impact.value,
            "confidence": self.confidence.value,
            "message": self.message,
            "package": self.package,
            "owner": self.owner,
            "file": self.file,
            "line": self.line,
            "fingerprint": self.fingerprint,
        }
