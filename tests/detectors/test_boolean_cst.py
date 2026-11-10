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
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.hygiene.boolean_cst import BooleanConstant, misuse
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import SPLICE_DARS

TRUE = lf.Expr(prim_con=lf.PrimCon.CON_TRUE)
FALSE = lf.Expr(prim_con=lf.PrimCon.CON_FALSE)
VAR = lf.Expr(var="c")


def _alt(pattern, body):
    if pattern == "_":
        return lf.CaseAlt(default=lf.Unit(), body=body)
    con = lf.PrimCon.CON_TRUE if pattern else lf.PrimCon.CON_FALSE
    return lf.CaseAlt(prim_con=con, body=body)


def _case(scrut, *alts):
    return lf.Case(scrut, tuple(_alt(p, b) for p, b in alts))


@pytest.mark.parametrize(
    "case,expected",
    [
        (_case(TRUE, (True, VAR), (False, VAR)), "condition is always True"),
        (_case(FALSE, (True, VAR), ("_", VAR)), "condition is always False"),
        (_case(VAR, (True, TRUE), (False, TRUE)), "result is always True regardless"),
        (_case(VAR, (True, FALSE), ("_", FALSE)), "result is always False regardless"),
        (_case(VAR, (True, TRUE), (False, FALSE)), "returns its own condition"),
        (_case(VAR, (True, TRUE), ("_", FALSE)), "returns its own condition"),
        (_case(VAR, (True, FALSE), (False, TRUE)), "negates its condition"),
        (_case(VAR, (True, VAR), (False, FALSE)), None),
        (_case(VAR, (True, TRUE)), None),
        (_case(VAR, ("_", TRUE)), None),
    ],
    ids=[
        "if-true",
        "if-false",
        "or-true",
        "and-false",
        "identity",
        "identity-default",
        "negation",
        "and-chain",
        "partial",
        "non-bool",
    ],
)
def test_misuse(case, expected):
    result = misuse(case)

    assert (result is None) if expected is None else expected in result


def test_detector_reports_example_violations(bool_index):
    found = [(f.owner, f.line, f.file) for f in BooleanConstant(bool_index).detect()]

    assert found == [
        ("Main:Vault.Close.update", 29, "Main.daml"),
        ("Main:Vault.Deposit.update", 20, "Main.daml"),
        ("Main:Vault.Touch.update", 36, "Main.daml"),
        ("Main:Vault.Withdraw.update", 10, "Main.daml"),
    ]


@pytest.mark.parametrize("dar_path", SPLICE_DARS, ids=[p.stem for p in SPLICE_DARS])
def test_detector_is_silent_on_splice(dar_path):
    assert BooleanConstant(PackageIndex(Dar.load(dar_path))).detect() == []
