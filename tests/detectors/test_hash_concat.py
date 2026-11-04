import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.validation.hash_concat import (
    HashConcatCollision,
    Joins,
    adjacent,
    let_values,
    listed,
)
from damlisk.lf.dar import Dar
from damlisk.lf.flow import FieldFlow
from damlisk.lf.index import PackageIndex
from tests.conftest import ROOT
from tests.lf.test_flow import app, helper, let, val, var

APPEND = lf.Expr(builtin="APPEND_TEXT")
IMPLODE = lf.Expr(builtin="IMPLODE_TEXT")
SHA = lf.Expr(builtin="SHA256_TEXT")
SEP = lf.Expr(prim_lit=lf.PrimLit(text="|"))
NIL = lf.Expr(nil=lf.Expr.Nil(None))
VALUES = dict([helper("sepThen", app(APPEND, SEP))])


def cons(items, tail=NIL):
    return lf.Expr(cons=lf.Expr.Cons(None, items, tail))


def label(part):
    if part.var is not None:
        return part.var
    if part.prim_lit is not None:
        return part.prim_lit.text
    return "?"


def names(parts):
    return [label(part) for part in parts]


@pytest.mark.parametrize(
    "expr,expected",
    [
        (let("msg", app(APPEND, var("a"), var("b")), var("msg")), ["msg"]),
        (let("a", var("x"), let("b", var("y"), var("b"))), ["a", "b"]),
        (var("x"), []),
    ],
    ids=["one-let", "nested-lets", "no-let"],
)
def test_let_values(expr, expected):
    assert list(let_values(expr)) == expected


@pytest.mark.parametrize(
    "items,tail,expected",
    [
        ((var("a"), var("b")), NIL, ["a", "b"]),
        ((var("a"),), var("rest"), ["a", "rest"]),
        ((), NIL, []),
    ],
    ids=["closed", "open-tail", "empty"],
)
def test_listed(items, tail, expected):
    assert names(listed(lf.Expr.Cons(None, items, tail))) == expected


@pytest.mark.parametrize(
    "parts,expected",
    [
        ([var("a"), var("b")], True),
        ([var("a"), SEP, var("b")], False),
        ([SEP, var("a")], False),
        ([var("a")], False),
    ],
    ids=["two-vars", "separated", "prefix", "single"],
)
def test_adjacent(parts, expected):
    assert adjacent(parts) is expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (app(APPEND, var("a"), var("b")), ["a", "b"]),
        (app(APPEND, var("a"), app(val("sepThen"), var("b"))), ["a", "|", "b"]),
        (app(IMPLODE, cons((var("a"), var("b")))), ["a", "b"]),
        (var("msg"), ["a", "b"]),
        (var("loop"), ["loop"]),
        (app(val("other"), var("a")), ["?"]),
    ],
    ids=["append", "partial-helper", "implode", "let-var", "self-bound", "opaque-call"],
)
def test_parts(expr, expected):
    bound = {"msg": app(APPEND, var("a"), var("b")), "loop": var("loop")}
    parts = Joins(FieldFlow(VALUES), bound).parts(expr)

    assert names(parts) == expected


@pytest.mark.parametrize(
    "fun,arg,expected",
    [
        (SHA, app(APPEND, var("a"), var("b")), True),
        (SHA, app(APPEND, var("a"), app(val("sepThen"), var("b"))), False),
        (SHA, app(APPEND, SEP, var("a")), False),
        (APPEND, app(APPEND, var("a"), var("b")), False),
    ],
    ids=["joined", "separated", "prefixed", "not-a-hash"],
)
def test_collides(fun, arg, expected):
    call = lf.Expr.App(fun, (arg,))

    assert Joins(FieldFlow(VALUES), {}).collides(call) is expected


def test_detector_reports_example_violations(hash_index):
    found = HashConcatCollision(hash_index).detect()
    rows = [(f.owner, f.line) for f in found]

    assert rows == [
        ("Main:Voucher.Commit.update", 47),
        ("Main:Voucher.Redeem.update", 16),
        ("Main:Voucher.Seal.update", 24),
    ]


@pytest.mark.parametrize(
    "dar_name",
    ["splice-amulet-0.1.24.dar", "splice-wallet-payments-0.1.24.dar", "splice-util-0.1.8.dar"],
    ids=["amulet", "wallet-payments", "util"],
)
def test_detector_is_silent_on_splice(dar_name):
    index = PackageIndex(Dar.load(ROOT / "examples" / "dars" / dar_name))

    assert HashConcatCollision(index).detect() == []
