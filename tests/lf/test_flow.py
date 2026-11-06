import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.flow import (
    THIS,
    FieldFlow,
    Usage,
    call_parts,
    create_arg,
    exercised,
    linked_fields,
    peel,
)

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


def exercise(cid):
    return lf.Expr(update=lf.Update(exercise=lf.Update.Exercise(None, "Archive", cid, var("u"))))


def iface_exercise(cid):
    exe = lf.Update.ExerciseInterface(None, cid, var("u"), None)
    return lf.Expr(update=lf.Update(exercise_interface=exe))


FOR_A = val("forA")
CONSUME_VALUES = dict([helper("archiveTok", lam(["cid"], exercise(var("cid"))))]) | FETCH_VALUES


@pytest.mark.parametrize(
    "expr,expected",
    [(exercise(var("c")), "c"), (iface_exercise(var("c")), "c"), (fetch(var("c")), None)],
    ids=["template", "interface", "fetch"],
)
def test_exercised(expr, expected):
    cid = exercised(expr.update)

    assert (cid.var if cid is not None else None) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [(lam(["a"], lam(["b"], var("x"))), "x"), (lam(["a"], var("y")), "y"), (var("z"), "z")],
    ids=["nested", "single", "no-lambda"],
)
def test_peel(expr, expected):
    assert peel(expr).var == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (exercise(proj("arg", "other")), {"other"}),
        (app(val("archiveTok"), proj("arg", "other")), {"other"}),
        (app(FOR_A, proj("arg", "others"), val("archiveTok")), {"others"}),
        (app(FOR_A, proj("arg", "others"), lam(["c"], exercise(var("c")))), {"others"}),
        (app(FOR_A, proj("arg", "others"), val("fetchTok")), set()),
        (app(FOR_A, proj("arg", "others"), val("useArg")), set()),
        (exercise(proj("this", "cid")), set()),
    ],
    ids=[
        "inline",
        "helper",
        "point-free-callback",
        "lambda-callback",
        "fetch-callback",
        "pure-helper",
        "contract-field",
    ],
)
def test_consumed(expr, expected):
    values = CONSUME_VALUES | VALUES

    assert FieldFlow(values).consumed(expr, "arg") == expected


def create(expr):
    return lf.Expr(update=lf.Update(create=lf.Update.Create(None, expr)))


def call(cid, arg):
    return lf.Expr(update=lf.Update(exercise=lf.Update.Exercise(None, "Pay", cid, arg)))


def soft_call(cid, arg):
    soft = lf.Update.SoftExercise(None, "Pay", cid, arg)
    return lf.Expr(update=lf.Update(soft_exercise=soft))


def iface_create(expr):
    made = lf.Update.CreateInterface(None, expr)
    return lf.Expr(update=lf.Update(create_interface=made))


SEND_VALUES = dict([helper("mint", lam(["rec"], create(var("rec"))))]) | VALUES


@pytest.mark.parametrize(
    "expr,created,called",
    [
        (create(proj("arg", "amount")), {"amount"}, set()),
        (app(val("mint"), proj("arg", "amount")), {"amount"}, set()),
        (call(proj("arg", "cid"), proj("arg", "payee")), set(), {"cid", "payee"}),
        (iface_exercise(proj("arg", "cid")), set(), {"cid"}),
        (create(proj("this", "amount")), set(), set()),
        (app(val("show"), proj("arg", "amount")), set(), set()),
    ],
    ids=["create", "create-helper", "exercise", "interface", "contract-field", "no-action"],
)
def test_created_and_called(expr, created, called):
    flow = FieldFlow(SEND_VALUES)

    assert flow.created(expr, "arg") == created
    assert flow.called(expr, "arg") == called


@pytest.mark.parametrize(
    "expr,expected",
    [
        (create(var("r")), "r"),
        (iface_create(var("r")), "r"),
        (call(var("c"), var("a")), None),
        (fetch(var("c")), None),
    ],
    ids=["create", "interface-create", "exercise", "fetch"],
)
def test_create_arg(expr, expected):
    record = create_arg(expr.update)

    assert (record.var if record is not None else None) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (call(var("c"), var("a")), ["c", "a"]),
        (iface_exercise(var("c")), ["c", "u"]),
        (soft_call(var("c"), var("a")), ["c", "a"]),
        (create(var("r")), []),
    ],
    ids=["exercise", "interface", "soft-exercise", "create"],
)
def test_call_parts(expr, expected):
    parts = call_parts(expr.update)

    assert [part.var for part in parts] == expected
