import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.tree import child_terms, find_all, mentions_var

TRUE = lf.Expr(prim_con=lf.PrimCon.CON_TRUE)
VAR = lf.Expr(var="x")
EQUAL = lf.Expr(builtin="EQUAL")
GET_TIME = lf.Update(get_time=lf.Unit())
LOC = lf.Location(
    lf.ModuleRef(lf.PackageRef("pkg"), lf.DottedName(("M",))), lf.Location.Range(4, 0, 4, 9)
)


def _case(scrut, *bodies):
    alts = [lf.CaseAlt(prim_con=lf.PrimCon.CON_TRUE, body=b) for b in bodies]
    return lf.Expr(case=lf.Case(scrut, tuple(alts)))


def _app(fun, *args):
    return lf.Expr(app=lf.Expr.App(fun, tuple(args)))


@pytest.mark.parametrize(
    "root,expected",
    [
        (VAR, []),
        (_app(EQUAL, VAR, TRUE), [EQUAL, VAR, TRUE]),
        (_case(VAR, TRUE, VAR), [VAR, TRUE, VAR]),
        (lf.Expr(update=GET_TIME), [GET_TIME]),
    ],
    ids=["leaf", "application", "case", "update"],
)
def test_child_terms(root, expected):
    assert [id(t) for t in child_terms(root)] == [id(t) for t in expected]


@pytest.mark.parametrize(
    "root,kind,count",
    [
        (_app(EQUAL, VAR, _app(EQUAL, TRUE)), lf.Expr.App, 2),
        (_case(VAR, TRUE, _case(TRUE, VAR)), lf.Case, 2),
        (_app(EQUAL, VAR, TRUE), lf.PrimCon, 1),
        (VAR, lf.Case, 0),
    ],
    ids=["nested-calls", "nested-cases", "constant", "missing"],
)
def test_find_all_counts(root, kind, count):
    assert len(find_all(root, kind)) == count


@pytest.mark.parametrize(
    "root,start,expected",
    [
        (_app(EQUAL, VAR), LOC, {4}),
        (_app(EQUAL, VAR), None, {None}),
        (lf.Expr(location=LOC, app=lf.Expr.App(EQUAL, (VAR,))), None, {4}),
    ],
    ids=["inherited", "unknown", "own-location"],
)
def test_find_all_keeps_location(root, start, expected):
    found = find_all(root, lf.Expr.App, start)

    assert {f.loc.range.start_line if f.loc else None for f in found} == expected


@pytest.mark.parametrize(
    "root,name,expected",
    [
        (VAR, "x", True),
        (_app(EQUAL, TRUE, _app(EQUAL, VAR)), "x", True),
        (_app(EQUAL, VAR), "y", False),
        (TRUE, "x", False),
    ],
    ids=["leaf", "nested", "other-name", "no-vars"],
)
def test_mentions_var(root, name, expected):
    assert mentions_var(root, name) is expected
