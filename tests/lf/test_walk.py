import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.walk import find, walk

TRUE = lf.Expr(prim_con=lf.PrimCon.CON_TRUE)
VAR = lf.Expr(var="x")
LOC = lf.Location(
    lf.ModuleRef(lf.PackageRef("pkg"), lf.DottedName(("M",))), lf.Location.Range(4, 0, 4, 9)
)


def _case(scrut, *bodies):
    alts = [lf.CaseAlt(prim_con=lf.PrimCon.CON_TRUE, body=b) for b in bodies]
    return lf.Expr(case=lf.Case(scrut, tuple(alts)))


def _app(fun, *args):
    return lf.Expr(app=lf.Expr.App(fun, tuple(args)))


@pytest.mark.parametrize(
    "root,kinds",
    [
        (VAR, ["var"]),
        (_app(lf.Expr(builtin="EQUAL"), VAR, TRUE), ["app", "builtin", "var", "prim_con"]),
        (_case(VAR, TRUE, VAR), ["case", "var", "prim_con", "var"]),
        (lf.Expr(update=lf.Update(get_time=lf.Unit())), ["update", "get_time"]),
        ([VAR, (TRUE,)], ["var", "prim_con"]),
        (None, []),
    ],
    ids=["leaf", "application", "case", "update", "sequences", "none"],
)
def test_walk_visits_nodes_in_preorder(root, kinds):
    assert [v.kind for v in walk(root)] == kinds


@pytest.mark.parametrize(
    "root,start,expected",
    [(VAR, None, None), (VAR, LOC, 4), (_case(VAR, TRUE), LOC, 4)],
    ids=["no-location", "inherited", "nested-inherited"],
)
def test_walk_propagates_locations(root, start, expected):
    lines = {v.loc.range.start_line if v.loc else None for v in walk(root, start)}

    assert lines == {expected}


@pytest.mark.parametrize(
    "root,kind,count",
    [(_case(VAR, TRUE, TRUE), "prim_con", 2), (_case(VAR, TRUE), "case", 1), (VAR, "app", 0)],
)
def test_find(root, kind, count):
    assert len(list(find(root, kind))) == count
