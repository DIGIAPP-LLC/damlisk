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

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.dar import LfPackage
from damlisk.output.finding import Confidence, Finding, Impact


def lf1_target(pkg: LfPackage) -> bool:
    """Return True if `pkg` was compiled for Daml-LF 1.x."""
    return pkg.lf_ver.startswith("1.")


class SdkVersion(AbstractDetector):
    ARGUMENT = "sdk-version"
    HELP = "DAR built for a Daml-LF 1.x target"
    IMPACT = Impact.INFORMATIONAL
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "SDK version"
    WIKI_DESCRIPTION = (
        "The main package of the DAR targets Daml-LF 1.x, built with a Daml 2.x SDK. Canton 3 "
        "and Splice run Daml-LF 2.x packages only, and LF 1.x lacks smart contract upgrades."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "A package built with SDK 2.10 (`--target=1.17`) cannot be uploaded to a Canton 3 "
        "participant, and its contracts cannot be upgraded in place to a fixed version."
    )
    WIKI_RECOMMENDATION = "Rebuild the package with a Daml 3.x SDK for a Daml-LF 2.x target."

    def _detect(self) -> list[Finding]:
        """Report the DAR when its main package targets Daml-LF 1.x."""
        main = self.index.dar.main
        if not lf1_target(main):
            return []
        sdk = self.index.dar.sdk or "unknown"
        message = f"{main.name}: built for Daml-LF {main.lf_ver} (SDK {sdk})"
        return [self.finding(main.name, message, None)]
