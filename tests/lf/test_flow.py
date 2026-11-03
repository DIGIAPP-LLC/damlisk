import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.flow import THIS, FieldFlow, Usage, linked_fields

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


def do_bind(name, bound, body):
    block = lf.Block([lf.Binding(lf.VarWithType(name, None), bound)], body)
    return lf.Expr(update=lf.Update(block=block))


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


HEAD = lf.Expr(
    val=lf.ValName(lf.ModuleRef(lf.PackageRef("std"), lf.DottedName(("DA", "List"))), ("head",))
)
PARTIAL_VALUES = dict([helper("firstOf", app(HEAD, var("xs")))])


@pytest.mark.parametrize(
    "expr,expected",
    [
        (app(HEAD, proj("arg", "winners")), {("winners", "head")}),
        (let("w", proj("arg", "winners"), app(HEAD, var("w"))), {("winners", "head")}),
        (app(HEAD, proj("this", "members")), set()),
        (app(EQUAL, proj("arg", "winners"), var("this")), set()),
        (do_bind("w", proj("arg", "winners"), app(HEAD, var("w"))), set()),
    ],
    ids=["direct", "let-alias", "contract-state", "not-partial", "ledger-result"],
)
def test_partial(expr, expected):
    uses = FieldFlow(PARTIAL_VALUES).partial(expr, "arg")

    assert {(use.field, use.function) for use in uses} == expected


def fetch(cid):
    return lf.Expr(update=lf.Update(fetch=lf.Update.Fetch(None, cid)))


FETCH_VALUES = dict([helper("fetchTok", lam(["cid"], fetch(var("cid"))))])
TEXT = lf.Expr(prim_lit=lf.PrimLit(text="USD"))


@pytest.mark.parametrize(
    "expr,expected",
    [
        (fetch(var("cid")), True),
        (app(val("fetchTok"), var("cid")), True),
        (app(val("useArg"), var("cid")), False),
        (var("cid"), False),
    ],
    ids=["inline", "helper", "other-helper", "not-a-call"],
)
def test_fetches(expr, expected):
    values = FETCH_VALUES | VALUES

    assert FieldFlow(values).fetches(expr) is expected


@pytest.mark.parametrize(
    "args,expected",
    [
        ([{"cid"}, {THIS}], {"cid"}),
        ([{"cid"}, {"owner"}], {"cid", "owner"}),
        ([{"cid"}, set()], set()),
        ([{"cid"}, {"cid"}], set()),
    ],
    ids=["with-contract", "with-argument", "with-constant", "with-itself"],
)
def test_linked_fields(args, expected):
    assert linked_fields([Usage(fields=fields) for fields in args]) == expected


def _fetched(check):
    use = proj("tok", "amount")
    return do_bind("tok", app(val("fetchTok"), proj("arg", "cid")), app(EQUAL, check, use))


@pytest.mark.parametrize(
    "expr,fetched,linked",
    [
        (_fetched(proj("this", "issuer")), {"cid"}, {"cid"}),
        (_fetched(TEXT), {"cid"}, set()),
        (do_bind("tok", app(val("fetchTok"), proj("arg", "cid")), TEXT), set(), set()),
        (do_bind("tok", app(val("fetchTok"), proj("this", "cid")), var("tok")), set(), set()),
    ],
    ids=["checked", "constant-only", "never-read", "contract-field"],
)
def test_fetch_usage(expr, fetched, linked):
    usage = FieldFlow(FETCH_VALUES).fetch_usage(expr, "arg", "this")

    assert usage.fetched == fetched
    assert usage.linked == linked


GE = lf.Expr(builtin="GREATER_EQ")


@pytest.mark.parametrize(
    "expr,expected",
    [
        (app(GE, proj("arg", "now"), proj("this", "unlock")), {"now"}),
        (let("t", proj("arg", "now"), app(GE, var("t"), var("x"))), {"now"}),
        (app(EQUAL, proj("arg", "now"), proj("this", "unlock")), set()),
        (app(GE, proj("this", "unlock"), var("x")), set()),
    ],
    ids=["direct", "let-alias", "equality", "contract-state"],
)
def test_ordered(expr, expected):
    assert FieldFlow(VALUES).ordered(expr, "arg") == expected
