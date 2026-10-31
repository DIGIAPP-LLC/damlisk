import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.detectors.hygiene.boolean_equal import BooleanEqual, misuse
from damlisk.lf.dar import Dar
from damlisk.lf.index import PackageIndex
from tests.conftest import SPLICE_DARS

TRUE = lf.Expr(prim_con=lf.PrimCon.CON_TRUE)
FALSE = lf.Expr(prim_con=lf.PrimCon.CON_FALSE)
VAR = lf.Expr(var="x")
EQUAL = lf.Expr(ty_app=lf.Expr.TyApp(lf.Expr(builtin="EQUAL"), ()))
LESS = lf.Expr(builtin="LESS")


def _method(module, name):
    pkg = lf.PackageRef("pkg")
    ref = lf.ModuleRef(pkg, lf.DottedName(segments=module.split(".")))
    return lf.Expr(val=lf.ValName(ref, (name,)))


NOT_EQ = _method("GHC.Classes", "$$c$u002f$u003d20")
EQ = _method("GHC.Classes", "$u003d$u003d")
OTHER = _method("Main", "$$c$u002f$u003d")


@pytest.mark.parametrize(
    "fun,args,expected",
    [
        (EQUAL, (VAR, TRUE), "(x == True), use `x`"),
        (EQUAL, (FALSE, VAR), "(x == False), use `not x`"),
        (NOT_EQ, (VAR, TRUE), "(x /= True), use `not x`"),
        (NOT_EQ, (FALSE,), "(x /= False), use `x`"),
        (EQ, (VAR, VAR, TRUE), "(x == True), use `x`"),
        (EQUAL, (VAR, VAR), None),
        (LESS, (VAR, TRUE), None),
        (OTHER, (VAR, TRUE), None),
    ],
    ids=[
        "equal-true",
        "equal-false",
        "not-equal-true",
        "partial-not-equal-false",
        "class-method",
        "no-constant",
        "other-builtin",
        "other-module",
    ],
)
def test_misuse(fun, args, expected):
    result = misuse(lf.Expr.App(fun, args))

    assert (result is None) if expected is None else expected in result


def test_detector_reports_example_violations(eq_index):
    found = [(f.owner, f.line, f.file) for f in BooleanEqual(eq_index).detect()]

    assert found == [
        ("Main:Ticket.Check.update", 27, "Main.daml"),
        ("Main:Ticket.Redeem.update", 14, "Main.daml"),
        ("Main:Ticket.Revoke.update", 20, "Main.daml"),
        ("Main:Ticket.precond", 12, "Main.daml"),
    ]


@pytest.mark.parametrize("dar_path", SPLICE_DARS, ids=[p.stem for p in SPLICE_DARS])
def test_detector_is_silent_on_splice(dar_path):
    assert BooleanEqual(PackageIndex(Dar.load(dar_path))).detect() == []
