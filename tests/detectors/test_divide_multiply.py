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

from damlisk.detectors.validation.divide_multiply import (
    DivideBeforeMultiply,
    divided_names,
    is_division,
    multiplies_quotient,
)
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT
from tests.lf.test_flow import app, let, var

DIV = lf.Expr(builtin="DIV_NUMERIC")
MUL = lf.Expr(builtin="MUL_NUMERIC")
FLOW = FieldFlow({})


@pytest.mark.parametrize(
    "expr,expected",
    [
        (app(DIV, var("a"), var("b")), True),
        (var("share"), True),
        (var("other"), False),
        (app(MUL, var("a"), var("b")), False),
        (lf.Expr(prim_con=lf.PrimCon.CON_TRUE), False),
    ],
    ids=["division", "divided-var", "plain-var", "multiplication", "constant"],
)
def test_is_division(expr, expected):
    assert is_division(FLOW, expr, {"share"}) is expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (let("share", app(DIV, var("a"), var("b")), var("share")), {"share"}),
        (let("q", app(DIV, var("a"), var("b")), let("r", var("q"), var("r"))), {"q", "r"}),
        (let("prod", app(MUL, var("a"), var("b")), var("prod")), set()),
    ],
    ids=["let-division", "alias-chain", "let-product"],
)
def test_divided_names(expr, expected):
    assert divided_names(FLOW, expr) == expected


@pytest.mark.parametrize(
    "fun,args,expected",
    [
        (MUL, (app(DIV, var("a"), var("b")), var("c")), True),
        (MUL, (var("c"), var("share")), True),
        (MUL, (var("a"), var("c")), False),
        (DIV, (app(MUL, var("a"), var("c")), var("b")), False),
    ],
    ids=["inline", "through-let", "no-division", "multiply-first"],
)
def test_multiplies_quotient(fun, args, expected):
    call = lf.Expr.App(fun, args)

    assert multiplies_quotient(FLOW, call, {"share"}) is expected


def test_detector_reports_example_violations(div_index):
    found = DivideBeforeMultiply(div_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [("Main:Pool.Fee.update", 19), ("Main:Pool.Payout.update", 11)]


@pytest.mark.parametrize(
    "dar_name,expected",
    [
        ("splice-amulet-0.1.24.dar", 5),
        ("splice-wallet-payments-0.1.24.dar", 0),
        ("splice-util-0.1.8.dar", 0),
    ],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name, expected):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert len(DivideBeforeMultiply(index).detect()) == expected
