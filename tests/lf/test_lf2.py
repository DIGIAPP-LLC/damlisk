import pytest
from dazl._gen.com.digitalasset.daml.lf.archive import daml_lf2_pb2 as pb
from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.builtins import (
    abs_name,
    arith_name,
    bool_const,
    cid_template,
    clock_name,
    compare_name,
    demangle,
    hash_name,
    index_name,
    is_compare,
    is_int,
    is_list,
    is_numeric,
    is_party,
    is_time,
    join_name,
    length_name,
    lf_name,
    lookup_name,
    loop_name,
    mentions_update,
    numeric_lit,
    order_name,
    partial_name,
    reads_time,
    text_lit,
    trace_name,
    unsafe_name,
    untyped,
)
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


def _prim(kind, *args):
    return lf.Type(prim=lf.Type.Prim(kind, args))


@pytest.mark.parametrize(
    "typ,expected",
    [
        (_prim(lf.PrimType.NUMERIC, _prim(lf.PrimType.INT64)), True),
        (_prim(lf.PrimType.INT64), False),
        (_prim(lf.PrimType.PARTY), False),
        (_prim(lf.PrimType.OPTIONAL, _prim(lf.PrimType.NUMERIC)), False),
    ],
    ids=["numeric", "int", "party", "optional-numeric"],
)
def test_is_numeric(typ, expected):
    assert is_numeric(typ) is expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (_val("DA.List", "head"), "head"),
        (lf.Expr(ty_app=lf.Expr.TyApp(_val("DA.Optional", "fromSome"), ())), "fromSome"),
        (_val("DA.List", "$u0021$u0021"), "!!"),
        (_val("DA.List.Total", "head"), None),
        (_val("DA.Optional", "fromSomeNote"), None),
        (lf.Expr(builtin="ERROR"), None),
    ],
    ids=["head", "typed-fromSome", "index", "total-head", "fromSomeNote", "builtin"],
)
def test_partial_name(fun, expected):
    assert partial_name(fun) == expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (lf.Expr(builtin="EQUAL"), "=="),
        (_val("DA.Internal.Prelude", "notElem"), "notElem"),
        (_val("GHC.Classes", "$$c$u002f$u003d3"), "/="),
        (_val("Market", "$$c$u003d$u003d15"), "=="),
        (_val("Market", "$u003d$u003d"), None),
        (_val("DA.List", "head"), None),
    ],
    ids=["equal", "not-elem", "not-equal-instance", "derived-instance", "user-operator", "other"],
)
def test_compare_name(fun, expected):
    assert compare_name(fun) == expected


UNIT = _prim(lf.PrimType.UNIT)
UPDATE_UNIT = _prim(lf.PrimType.UPDATE, UNIT)


@pytest.mark.parametrize(
    "typ,expected",
    [
        (UPDATE_UNIT, True),
        (_prim(lf.PrimType.LIST, UPDATE_UNIT), True),
        (lf.Type(con=lf.Type.Con(None, (UPDATE_UNIT,))), True),
        (lf.Type(var=lf.Type.Var("m", (UPDATE_UNIT,))), True),
        (lf.Type(syn=lf.Type.Syn(None, (UPDATE_UNIT,))), True),
        (lf.Type(forall=lf.Type.Forall((), UPDATE_UNIT)), True),
        (lf.Type(struct=lf.Type.Struct((lf.FieldWithType("f", UPDATE_UNIT),))), True),
        (_prim(lf.PrimType.LIST, _prim(lf.PrimType.INT64)), False),
        (lf.Type(nat=10), False),
        (UNIT, False),
    ],
    ids=[
        "update",
        "list-of-updates",
        "con-argument",
        "var-argument",
        "synonym",
        "forall-body",
        "struct-field",
        "list-of-ints",
        "nat",
        "unit",
    ],
)
def test_mentions_update(typ, expected):
    assert mentions_update(typ) is expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (lf.Expr(builtin="LESS"), "<"),
        (lf.Expr(builtin="GREATER_EQ"), ">="),
        (_val("DA.Internal.LF", "$$c$u003e$u003d1"), ">="),
        (_val("GHC.Classes", "$u003c$u003d"), "<="),
        (_val("Main", "$u003c"), None),
        (lf.Expr(builtin="EQUAL"), None),
        (lf.Expr(var="x"), None),
    ],
    ids=["less", "greater-eq", "time-instance", "class-method", "user-op", "equal", "var"],
)
def test_order_name(fun, expected):
    assert order_name(fun) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (_prim(lf.PrimType.TIMESTAMP), True),
        (_prim(lf.PrimType.DATE), False),
        (_prim(lf.PrimType.OPTIONAL, _prim(lf.PrimType.TIMESTAMP)), False),
    ],
    ids=["time", "date", "optional-time"],
)
def test_is_time(typ, expected):
    assert is_time(typ) is expected


@pytest.mark.parametrize(
    "module,name,expected",
    [
        ("DA.Internal.LF", "$$cgetTime", True),
        ("DA.Time", "isLedgerTimeLT", True),
        ("DA.Assert", "assertWithinDeadline", True),
        ("DA.Time", "addRelTime", False),
    ],
    ids=["get-time", "ledger-time-lt", "within-deadline", "other"],
)
def test_reads_time(module, name, expected):
    assert reads_time(_val(module, name).val) is expected


def _ty_abs(expr):
    return lf.Expr(ty_abs=lf.Expr.TyAbs((), lf.Expr(ty_app=lf.Expr.TyApp(expr, ()))))


@pytest.mark.parametrize(
    "fun,expected",
    [
        (_ty_abs(lf.Expr(builtin="LESS")), "LESS"),
        (lf.Expr(ty_app=lf.Expr.TyApp(_ty_abs(lf.Expr(builtin="EQUAL")), ())), "EQUAL"),
        (lf.Expr(builtin="GREATER"), "GREATER"),
    ],
    ids=["type-abstraction", "applied-abstraction", "plain"],
)
def test_untyped(fun, expected):
    assert untyped(fun).builtin == expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (_val("GHC.Num", "$$cabs1"), "abs"),
        (_val("GHC.Num", "abs"), "abs"),
        (_val("GHC.Num", "$$c-"), None),
        (_val("Main", "abs"), None),
        (lf.Expr(var="abs"), None),
    ],
    ids=["instance", "class-method", "minus", "user-abs", "var"],
)
def test_abs_name(fun, expected):
    assert abs_name(fun) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (lf.Expr(prim_lit=lf.PrimLit(numeric="0.0001000000")), "0.0001"),
        (lf.Expr(prim_lit=lf.PrimLit(numeric="10.0000000000")), "10"),
        (lf.Expr(prim_lit=lf.PrimLit(numeric="0.0000000000")), None),
        (lf.Expr(prim_lit=lf.PrimLit(int64=1)), None),
        (lf.Expr(var="eps"), None),
    ],
    ids=["tolerance", "whole", "zero", "int", "var"],
)
def test_numeric_lit(expr, expected):
    assert numeric_lit(expr) == expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (lf.Expr(builtin="MUL_NUMERIC"), "*"),
        (lf.Expr(builtin="DIV_INT64"), "/"),
        (_val("GHC.Num", "$$c*"), "*"),
        (_val("GHC.Num", "$$c/"), "/"),
        (_val("GHC.Num", "$$c+"), None),
        (_val("Main", "$$c*"), None),
        (lf.Expr(builtin="ADD_NUMERIC"), None),
    ],
    ids=["mul-builtin", "div-builtin", "mul-method", "div-method", "plus", "user-op", "add"],
)
def test_arith_name(fun, expected):
    assert arith_name(fun) == expected


TOKEN = lf.TypeConName(
    lf.ModuleRef(lf.PackageRef("pkg"), lf.DottedName(segments=("Main",))), ("Token",)
)


@pytest.mark.parametrize(
    "typ,expected",
    [
        (_prim(lf.PrimType.CONTRACT_ID, lf.Type(con=lf.Type.Con(TOKEN, ()))), TOKEN),
        (
            _prim(
                lf.PrimType.LIST,
                _prim(lf.PrimType.CONTRACT_ID, lf.Type(con=lf.Type.Con(TOKEN, ()))),
            ),
            TOKEN,
        ),
        (
            _prim(
                lf.PrimType.OPTIONAL,
                _prim(lf.PrimType.CONTRACT_ID, lf.Type(con=lf.Type.Con(TOKEN, ()))),
            ),
            None,
        ),
        (_prim(lf.PrimType.CONTRACT_ID, lf.Type(var=lf.Type.Var("t", ()))), None),
        (_prim(lf.PrimType.PARTY), None),
    ],
    ids=["cid", "cid-list", "optional-cid", "generic-cid", "party"],
)
def test_cid_template(typ, expected):
    assert cid_template(typ) == expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (lf.Expr(builtin="SHA256_TEXT"), "sha256"),
        (lf.Expr(builtin="KECCAK256_TEXT"), "keccak256"),
        (_val("DA.Text", "sha256"), "sha256"),
        (_val("Main", "sha256"), None),
        (lf.Expr(builtin="APPEND_TEXT"), None),
        (lf.Expr(var="sha256"), None),
    ],
    ids=["builtin", "keccak", "library", "user-sha256", "append", "var"],
)
def test_hash_name(fun, expected):
    assert hash_name(fun) == expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (lf.Expr(builtin="APPEND_TEXT"), "<>"),
        (lf.Expr(builtin="IMPLODE_TEXT"), "implode"),
        (lf.Expr(builtin="SHA256_TEXT"), None),
        (_val("DA.Text", "implode"), None),
    ],
    ids=["append", "implode", "hash", "val"],
)
def test_join_name(fun, expected):
    assert join_name(fun) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (lf.Expr(prim_lit=lf.PrimLit(text="|")), "|"),
        (lf.Expr(prim_lit=lf.PrimLit(int64=1)), None),
        (lf.Expr(var="sep"), None),
    ],
    ids=["text", "int", "var"],
)
def test_text_lit(expr, expected):
    assert text_lit(expr) == expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (_val("DA.Internal.LF", "getTime"), "getTime"),
        (_val("DA.Internal.LF", "$$cgetTime"), "getTime"),
        (_val("DA.Time", "isLedgerTimeLT"), None),
        (_val("Main", "getTime"), None),
        (lf.Expr(var="now"), None),
    ],
    ids=["class-method", "instance", "ledger-time-test", "user-value", "var"],
)
def test_clock_name(fun, expected):
    assert clock_name(fun) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (lf.Type(prim=lf.Type.Prim(lf.PrimType.INT64, ())), True),
        (lf.Type(prim=lf.Type.Prim(lf.PrimType.NUMERIC, ())), False),
        (lf.Type(var=lf.Type.Var("a", ())), False),
    ],
    ids=["int", "numeric", "type-var"],
)
def test_is_int(typ, expected):
    assert is_int(typ) is expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (lf.Expr(builtin="COERCE_CONTRACT_ID"), "coerceContractId"),
        (_val("DA.Internal.LF", "coerceContractId"), "coerceContractId"),
        (_val("DA.Internal.Interface", "unsafeFromInterface"), "unsafeFromInterface"),
        (_val("Main", "$$cunsafeFromInterface1"), "unsafeFromInterface"),
        (
            lf.Expr(unsafe_from_interface=lf.Expr.UnsafeFromInterface(None, None, None, None)),
            "unsafeFromInterface",
        ),
        (lf.Expr(from_any=lf.Expr.FromAny(None, None)), "fromAny"),
        (_val("DA.Internal.Interface", "toInterfaceContractId"), None),
        (lf.Expr(builtin="EQUAL"), None),
    ],
    ids=[
        "coerce-builtin",
        "coerce-value",
        "unsafe-value",
        "unsafe-instance-method",
        "unsafe-node",
        "from-any-node",
        "upcast",
        "other-builtin",
    ],
)
def test_unsafe_name(expr, expected):
    assert unsafe_name(expr) == expected


@pytest.mark.parametrize(
    "expr,expected",
    [
        (lf.Expr(builtin="TRACE"), "TRACE"),
        (_val("DA.Internal.Prelude", "trace"), "trace"),
        (_val("DA.Internal.Prelude", "debugRaw"), "debugRaw"),
        (_val("Main", "trace"), None),
        (lf.Expr(builtin="APPEND_TEXT"), None),
    ],
    ids=["builtin", "trace", "debug-raw", "user-value", "other-builtin"],
)
def test_trace_name(expr, expected):
    assert trace_name(expr) == expected


@pytest.mark.parametrize(
    "typ,expected",
    [
        (lf.Type(prim=lf.Type.Prim(lf.PrimType.PARTY, ())), True),
        (lf.Type(prim=lf.Type.Prim(lf.PrimType.TEXT, ())), False),
        (lf.Type(var=lf.Type.Var("a", ())), False),
    ],
    ids=["party", "text", "type-var"],
)
def test_is_party(typ, expected):
    assert is_party(typ) is expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (_val("DA.List", "$u0021$u0021"), "!!"),
        (_val("DA.List", "head"), None),
        (_val("Main", "$u0021$u0021"), None),
        (lf.Expr(var="xs"), None),
    ],
    ids=["list-index", "other-list", "user-value", "var"],
)
def test_index_name(fun, expected):
    assert index_name(fun) == expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (_val("DA.Map", "lookup"), "lookup"),
        (_val("DA.TextMap", "member"), "member"),
        (lf.Expr(builtin="GENMAP_LOOKUP"), "lookup"),
        (_val("DA.Map", "insert"), None),
        (lf.Expr(builtin="GENMAP_INSERT"), None),
        (lf.Expr(var="m"), None),
    ],
    ids=["map-lookup", "textmap-member", "genmap-builtin", "map-insert", "genmap-insert", "var"],
)
def test_lookup_name(fun, expected):
    assert lookup_name(fun) == expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (_val("DA.Foldable", "forA_"), "forA_"),
        (_val("DA.Internal.Prelude", "mapA"), "mapA"),
        (_val("DA.Internal.Prelude", "foldl"), "foldl"),
        (_val("Main", "forA"), None),
        (_val("GHC.Base", "map"), None),
        (lf.Expr(var="f"), None),
    ],
    ids=["for-a", "map-a", "fold", "user-value", "pure-map", "var"],
)
def test_loop_name(fun, expected):
    assert loop_name(fun) == expected


def _prim(prim, *args):
    return lf.Type(prim=lf.Type.Prim(prim, args))


@pytest.mark.parametrize(
    "typ,expected",
    [
        (_prim(lf.PrimType.LIST, _prim(lf.PrimType.PARTY)), True),
        (_prim(lf.PrimType.OPTIONAL, _prim(lf.PrimType.LIST, _prim(lf.PrimType.PARTY))), True),
        (_prim(lf.PrimType.OPTIONAL, _prim(lf.PrimType.PARTY)), False),
        (_prim(lf.PrimType.TEXT), False),
    ],
    ids=["list", "optional-list", "optional-party", "text"],
)
def test_is_list(typ, expected):
    assert is_list(typ) is expected


@pytest.mark.parametrize(
    "fun,expected",
    [
        (_val("DA.Internal.Prelude", "length"), "length"),
        (_val("DA.Foldable", "$$dmlength"), "length"),
        (_val("DA.Text", "length"), None),
        (lf.Expr(var="n"), None),
    ],
    ids=["prelude", "foldable-default", "text-length", "var"],
)
def test_length_name(fun, expected):
    assert length_name(fun) == expected
