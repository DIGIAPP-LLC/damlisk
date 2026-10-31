import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.flow import FieldFlow

REF = lf.ModuleRef(lf.PackageRef("pkg"), lf.DottedName(segments=("Main",)))
EQUAL = lf.Expr(builtin="EQUAL")


def var(name):
    return lf.Expr(var=name)


def proj(record, name):
    return lf.Expr(rec_proj=lf.Expr.RecProj(None, name, var(record)))


def app(fun, *args):
    return lf.Expr(app=lf.Expr.App(fun, args))


def lam(params, body):
    return lf.Expr(abs=lf.Expr.Abs([lf.VarWithType(p, None) for p in params], body))


def let(name, bound, body):
    return lf.Expr(let=lf.Block([lf.Binding(lf.VarWithType(name, None), bound)], body))


def val(name):
    return lf.Expr(val=lf.ValName(REF, (name,)))


def helper(name, expr):
    return lf.ValName(REF, (name,)), lf.DefValue(
        lf.DefValue.NameWithType((name,), None), expr, True, False
    )


VALUES = dict(
    [
        helper("useArg", lam(["this", "arg"], proj("arg", "party"))),
        helper("useThis", lam(["this"], let("x", proj("this", "owner"), lam(["arg"], var("x"))))),
        helper("isEq", EQUAL),
    ]
)


@pytest.mark.parametrize(
    "expr,fields,compared",
    [
        (var("arg"), {"*"}, set()),
        (proj("arg", "party"), {"party"}, set()),
        (proj("this", "owner"), set(), set()),
        (let("p", proj("arg", "party"), app(val("show"), var("p"))), {"party"}, set()),
        (app(EQUAL, proj("arg", "party"), proj("this", "owner")), {"party"}, {"party"}),
        (app(val("isEq"), proj("arg", "party"), var("this")), {"party"}, {"party"}),
        (app(val("useArg"), var("this"), var("arg")), {"party"}, set()),
        (app(val("useThis"), var("this"), var("arg")), set(), set()),
        (app(lam(["t", "ds"], var("t")), var("this"), var("arg")), set(), set()),
    ],
    ids=[
        "bare-var",
        "projection",
        "other-var",
        "let-alias",
        "builtin-compare",
        "helper-compare",
        "helper-uses-arg",
        "helper-ignores-arg",
        "inline-lambda-ignores-arg",
    ],
)
def test_trace(expr, fields, compared):
    flow = FieldFlow(VALUES)

    assert flow.fields(expr, "arg") == fields
    assert flow.compared(expr, "arg") == compared
