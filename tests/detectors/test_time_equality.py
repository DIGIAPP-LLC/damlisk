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

from damlisk.detectors.validation.time_equality import (
    TimeEquality,
    clock_names,
    reads_now,
    time_equality,
)
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT
from tests.lf.test_flow import app, do_bind, helper, let, val, var
from tests.lf.test_lf2 import _val

CLOCK = _val("DA.Internal.LF", "getTime")
EQUAL = lf.Expr(builtin="EQUAL")
LESS = lf.Expr(builtin="LESS")
EPOCH = lf.Expr(prim_lit=lf.PrimLit(timestamp=0))
GET_TIME = lf.Expr(update=lf.Update(get_time=lf.Unit()))
VALUES = dict([helper("now", app(CLOCK, var("dict"))), helper("isEpoch", app(EQUAL, EPOCH))])
FLOW = FieldFlow(VALUES)


@pytest.mark.parametrize(
    "bound,expected",
    [
        (GET_TIME, True),
        (val("now"), True),
        (app(CLOCK, var("dict")), True),
        (lf.Expr(update=lf.Update(pure=lf.Pure(None, var("t")))), False),
        (var("t"), False),
    ],
    ids=["builtin", "helper", "library-call", "other-update", "var"],
)
def test_reads_now(bound, expected):
    assert reads_now(FLOW, bound) is expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (do_bind("now", val("now"), var("now")), {"now"}),
        (do_bind("now", GET_TIME, let("t", var("now"), var("t"))), {"now", "t"}),
        (do_bind("x", var("y"), var("x")), set()),
    ],
    ids=["bind", "alias", "no-clock"],
)
def test_clock_names(expr, expected):
    assert clock_names(FLOW, expr) == expected


@pytest.mark.parametrize(
    "fun,args,expected",
    [
        (EQUAL, (var("now"), var("closes")), "=="),
        (val("isEpoch"), (var("now"),), "=="),
        (val("isEpoch"), (var("t"),), None),
        (LESS, (var("now"), var("closes")), None),
        (EQUAL, (var("a"), var("b")), None),
    ],
    ids=["equal", "partial-helper", "partial-other", "ordering", "no-clock"],
)
def test_time_equality(fun, args, expected):
    call = lf.Expr.App(fun, args)

    assert time_equality(FLOW, call, {"now"}) == expected


def test_detector_reports_example_violations(clock_index):
    found = TimeEquality(clock_index).detect()
    rows = [(f.owner, f.line, f.message) for f in found]

    assert rows == [
        ("Main:Auction.Bid.update", 19, "Main:Auction.Bid.update: ledger time compared with `/=`"),
        (
            "Main:Auction.Close.update",
            13,
            "Main:Auction.Close.update: ledger time compared with `==`",
        ),
    ]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert TimeEquality(index).detect() == []
