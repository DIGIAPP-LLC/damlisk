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

from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.abstract_detector import AbstractDetector
from damlisk.lf.builtins import text_lit
from damlisk.lf.index import Scope
from damlisk.lf.tree import all_terms
from damlisk.output.finding import Confidence, Finding, Impact

BIDI = frozenset("‪‫‬‭‮⁦⁧⁨⁩")


def bidi_chars(text: str) -> list[str]:
    """Return the bidirectional control characters in `text` as code points (`U+202E`)."""
    found = sorted({char for char in text if char in BIDI})
    return [f"U+{ord(char):04X}" for char in found]


def bidi_lines(scope: Scope) -> list[lf.Location]:
    """Return the source lines of a module that contain a bidirectional control character."""
    locs = []
    for no, line in enumerate(scope.lines):
        cols = [col for col, char in enumerate(line) if char in BIDI]
        if cols:
            rng = lf.Location.Range(no, cols[0], no, cols[0] + 1)
            locs.append(lf.Location(scope.ref, rng))
    return locs


class Rtlo(AbstractDetector):
    ARGUMENT = "rtlo"
    HELP = "Bidirectional control character (right-to-left override) in source or Text"
    IMPACT = Impact.HIGH
    CONFIDENCE = Confidence.HIGH
    WIKI_TITLE = "Right-to-left override"
    WIKI_DESCRIPTION = (
        "U+202E and the other Unicode bidirectional control characters reorder the text "
        "around them when it is displayed. In a comment they make the source a reviewer reads "
        "differ from the code that runs; in a `Text` value they make a name or label shown to "
        "users differ from its content."
    )
    WIKI_EXPLOIT_SCENARIO = (
        '`note = "user\\x202Etxt.exe"` is displayed as `userexe.txt`, so a wallet shows a '
        "harmless-looking name for a value that the contract and its counterparties treat as "
        "something else."
    )
    WIKI_RECOMMENDATION = (
        "Remove bidirectional control characters from sources and literals; reject them in "
        "`Text` fields that are shown to users."
    )

    def _detect(self) -> list[Finding]:
        """Report each source line and each `Text` literal with a bidirectional control char."""
        findings = []
        scopes = self.index.scopes(self.index.dar.main)
        for scope in scopes:
            owner = str(scope.module.name)
            locs = bidi_lines(scope)
            for loc in locs:
                line = scope.lines[loc.range.start_line]
                names = ", ".join(bidi_chars(line))
                message = f"{owner}: bidirectional control character {names} in source"
                findings.append(self.finding(owner, message, loc))
        bodies = self.index.bodies()
        for body in bodies:
            terms = all_terms(body.expr, body.loc)
            for term in terms:
                if not isinstance(term.node, lf.Expr):
                    continue
                text = text_lit(term.node)
                chars = bidi_chars(text) if text else []
                if chars:
                    names = ", ".join(chars)
                    message = f"{body.owner}: Text literal contains {names}"
                    findings.append(self.finding(body.owner, message, term.loc))
        return findings
