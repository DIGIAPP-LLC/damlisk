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

from damlisk.detectors.validation.ignored_optional import (
    IgnoredOptional,
    forced,
    ignored,
    is_optional,
)
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from damlisk.lf.tree import all_terms
from tests.conftest import ROOT

FROM_SOME = lf.ValName(
    lf.ModuleRef(lf.PackageRef("std"), lf.DottedName(("DA", "Optional"))), ("fromSome",)
)


def prim(kind, *args):
    return lf.Type(prim=lf.Type.Prim(kind, args))


def apply(fun, arg):
    return lf.Expr(app=lf.Expr.App(fun, (arg,)))


def issues_of(index, choice):
    owner = f"Main:Registry.{choice}.update"
    found = []
    bodies = [b for b in index.bodies() if b.owner == owner]
    for body in bodies:
        terms = all_terms(body.expr)
        for term in terms:
            node = term.node
            if isinstance(node, lf.Update) and node.block is not None:
                found.extend(ignored(node.block))
    return found


@pytest.mark.parametrize(
    "typ,expected",
    [
        (prim(lf.PrimType.OPTIONAL, prim(lf.PrimType.PARTY)), True),
        (prim(lf.PrimType.LIST, prim(lf.PrimType.PARTY)), False),
        (prim(lf.PrimType.PARTY), False),
    ],
    ids=["optional", "list", "party"],
)
def test_is_optional(typ, expected):
    assert is_optional(typ) is expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (apply(lf.Expr(val=FROM_SOME), lf.Expr(var="r")), True),
        (apply(lf.Expr(val=FROM_SOME), lf.Expr(var="other")), False),
        (lf.Expr(var="r"), False),
    ],
    ids=["forced", "other-var", "plain-use"],
)
def test_forced(expr, expected):
    assert forced(expr, "r") is expected


@pytest.mark.parametrize(
    "choice,expected",
    [
        ("CheckOnly", ["`found` is never used"]),
        ("ForceFind", ["`found` is forced with fromSome"]),
        ("ForceHelper", ["`found` is forced with fromSome"]),
        ("Matched", []),
        ("Noted", []),
        ("Defaulted", []),
    ],
    ids=["unused", "forced", "helper-forced", "matched", "from-some-note", "from-optional"],
)
def test_ignored(optional_index, choice, expected):
    assert issues_of(optional_index, choice) == expected


def test_detector_reports_example_violations(optional_index):
    found = IgnoredOptional(optional_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [
        ("Main:Registry.CheckOnly.update", 18),
        ("Main:Registry.ForceFind.update", 26),
        ("Main:Registry.ForceHelper.update", 34),
    ]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert IgnoredOptional(index).detect() == []
