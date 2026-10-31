import pytest
from dazl._gen.com.digitalasset.daml.lf.archive import daml_lf2_pb2 as pb
from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.builtins import bool_const, demangle, is_compare, lf_name
from damlisk.lf.lf2 import Parser23


def _builtin(name: str):
    return pb.Type(builtin=pb.Type.Builtin(builtin=pb.BuiltinType.Value(name)))


def _parser() -> Parser23:
    parser = Parser23(lf.PackageRef("pkg"))
    parser.interned_dotted_names.append(("M",))
    parser.imports = ["pkg2"]
    parser.kinds = [pb.Kind(star=pb.Unit())]
    parser.exprs = [pb.Expr(builtin_con=pb.BuiltinCon.Value("CON_UNIT"))]
    return parser


@pytest.mark.parametrize(
    "method,message,check",
    [
        (
            "parse_Type",
            pb.Type(tapp=pb.Type.TApp(lhs=_builtin("LIST"), rhs=_builtin("PARTY"))),
            lambda result: len(result.prim.args) == 1,
        ),
        ("parse_Kind", pb.Kind(interned_kind=0), lambda result: result.star is not None),
        ("parse_Expr", pb.Expr(interned_expr=0), lambda result: result.prim_con is not None),
        ("parse_Update", pb.Update(), lambda result: result is None),
        (
            "parse_ModuleId",
            pb.ModuleId(package_id=pb.SelfOrImportedPackageId(package_import_id=0)),
            lambda result: str(result) == "pkg2:M",
        ),
    ],
    ids=["type-application", "interned-kind", "interned-expr", "unknown-update", "package-import"],
)
def test_parser_reads_lf2_messages(method, message, check):
    assert check(getattr(_parser(), method)(message))


@pytest.mark.parametrize(
    "number,expected",
    [(1, "ERROR"), (2, "EQUAL"), (7, "ADD_INT64"), (34, "APPEND_TEXT"), (99999, "UNKNOWN_99999")],
)
def test_builtin_functions_use_lf2_numbering(number, expected):
    assert _parser().parse_BuiltinFunction(number) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("DATE", lf.PrimType.DATE),
        ("NUMERIC", lf.PrimType.NUMERIC),
        ("PARTY", lf.PrimType.PARTY),
        ("FAILURE_CATEGORY", "FAILURE_CATEGORY"),
    ],
)
def test_builtin_types_use_lf2_numbering(name, expected):
    assert _parser().parse_BuiltinType(pb.BuiltinType.Value(name)) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("ADD_INT64", "ADD_INT64"),
        (lf.BuiltinFunction.EQUAL, "EQUAL"),
        (lf.PrimType.PARTY, "PARTY"),
        (7, "7"),
    ],
    ids=["lf2-string", "lf1-builtin", "prim-type", "raw-int"],
)
def test_lf_name(value, expected):
    assert lf_name(value) == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("$$c$u002f$u003d20", "$c/=20"),
        ("$u003d$u003d", "=="),
        ("$$$$sc_Ticket_8", "$$sc_Ticket_8"),
        ("plain", "plain"),
    ],
    ids=["instance-method", "class-method", "double-dollar", "plain"],
)
def test_demangle(name, expected):
    assert demangle(name) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (lf.Expr(prim_con=lf.PrimCon.CON_TRUE), "True"),
        (lf.Expr(prim_con=lf.PrimCon.CON_FALSE), "False"),
        (lf.Expr(prim_con=lf.PrimCon.CON_UNIT), None),
        (lf.Expr(var="x"), None),
    ],
    ids=["true", "false", "unit", "var"],
)
def test_bool_const(expr, expected):
    assert bool_const(expr) == expected


def _val(module, name):
    ref = lf.ModuleRef(lf.PackageRef("pkg"), lf.DottedName(segments=tuple(module.split("."))))
    return lf.Expr(val=lf.ValName(ref, (name,)))


@pytest.mark.parametrize(
    "fun,expected",
    [
        (lf.Expr(builtin="EQUAL"), True),
        (lf.Expr(ty_app=lf.Expr.TyApp(_val("DA.Internal.Prelude", "elem"), ())), True),
        (_val("GHC.Classes", "$$dm$u002f$u003d"), True),
        (_val("DA.Internal.Prelude", "map"), False),
        (lf.Expr(builtin="LESS"), False),
    ],
    ids=["equal", "elem", "default-not-equal", "other-function", "other-builtin"],
)
def test_is_compare(fun, expected):
    assert is_compare(fun) is expected
