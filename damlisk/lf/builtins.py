import re
from decimal import Decimal
from enum import Enum

from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.util import module_local_name, module_name

BOOLS = {lf.PrimCon.CON_TRUE: "True", lf.PrimCon.CON_FALSE: "False"}
ESCAPE_RE = re.compile(r"\$(?:\$|u([0-9a-f]{4}))")
EQ_RE = re.compile(r"^(?:\$c|\$dm)?(==|/=)\d*$")
ORDER_RE = re.compile(r"^(?:\$c|\$dm)?(<|<=|>|>=)\d*$")
ORDERS = {"LESS": "<", "LESS_EQ": "<=", "GREATER": ">", "GREATER_EQ": ">="}
EQ_MODULE = "GHC.Classes"
NUM_MODULE = "GHC.Num"
ABS_RE = re.compile(r"^(?:\$c)?abs\d*$")
ARITH_RE = re.compile(r"^(?:\$c)?(\*|/)\d*$")
ARITH = {"MUL_INT64": "*", "MUL_NUMERIC": "*", "DIV_INT64": "/", "DIV_NUMERIC": "/"}
TIME_READS = {
    ("DA.Internal.LF", "getTime"),
    ("DA.Internal.LF", "$cgetTime"),
    ("DA.Time", "isLedgerTimeLT"),
    ("DA.Time", "isLedgerTimeLE"),
    ("DA.Time", "isLedgerTimeGT"),
    ("DA.Time", "isLedgerTimeGE"),
    ("DA.Assert", "assertWithinDeadline"),
    ("DA.Assert", "assertDeadlineExceeded"),
}
MEMBERSHIP = {("DA.Internal.Prelude", "elem"), ("DA.Internal.Prelude", "notElem")}
PARTIAL = {
    ("DA.List", "head"),
    ("DA.List", "tail"),
    ("DA.List", "last"),
    ("DA.List", "init"),
    ("DA.List", "!!"),
    ("DA.List", "foldl1"),
    ("DA.List", "foldr1"),
    ("DA.Foldable", "maximum"),
    ("DA.Foldable", "minimum"),
    ("DA.Foldable", "foldl1"),
    ("DA.Foldable", "foldr1"),
    ("DA.Optional", "fromSome"),
    ("DA.Maybe", "fromJust"),
    ("DA.Either", "fromLeft"),
    ("DA.Either", "fromRight"),
}


def lf_name(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Enum):
        return value.name
    return str(value)


def is_numeric(typ: lf.Type) -> bool:
    return typ.prim is not None and typ.prim.prim == lf.PrimType.NUMERIC


def type_args(typ: lf.Type) -> list[lf.Type]:
    """Return the types nested directly inside `typ` (type arguments, fields, bodies)."""
    if typ.prim is not None:
        return list(typ.prim.args)
    if typ.con is not None:
        return list(typ.con.args)
    if typ.var is not None:
        return list(typ.var.args)
    if typ.syn is not None:
        return list(typ.syn.args)
    if typ.forall is not None:
        return [typ.forall.body]
    if typ.struct is not None:
        return [field.type for field in typ.struct.fields]
    return []


def mentions_update(typ: lf.Type) -> bool:
    """Return True if `typ` is or contains the `Update` type, e.g. `[Update ()]`."""
    if typ.prim is not None and typ.prim.prim == lf.PrimType.UPDATE:
        return True
    nested = type_args(typ)
    for arg in nested:
        if mentions_update(arg):
            return True
    return False


def cid_template(typ: lf.Type) -> lf.TypeConName | None:
    """Return `T` for `ContractId T` or `[ContractId T]`, or None for other types."""
    if typ.prim is None or not typ.prim.args:
        return None
    inner = typ.prim.args[0]
    if typ.prim.prim == lf.PrimType.LIST:
        return cid_template(inner)
    if typ.prim.prim != lf.PrimType.CONTRACT_ID or inner.con is None:
        return None
    return inner.con.tycon


def type_owner(name: lf.TypeConName) -> str:
    """Return a type's owner string in the `Module:Type` form used by template owners."""
    return f"{module_name(name)}:{module_local_name(name)}"


def bool_const(expr: lf.Expr) -> str | None:
    if expr.prim_con is None:
        return None
    return BOOLS.get(expr.prim_con)


def unescape(match: re.Match[str]) -> str:
    code = match[1]
    return chr(int(code, 16)) if code else "$"


def demangle(name: str) -> str:
    return ESCAPE_RE.sub(unescape, name)


def untyped(fun: lf.Expr) -> lf.Expr:
    """Return `fun` without its type applications and type abstractions."""
    while True:
        if fun.ty_app is not None:
            fun = fun.ty_app.expr
        elif fun.ty_abs is not None:
            fun = fun.ty_abs.body
        else:
            return fun


def qual_name(val: lf.ValName) -> tuple[str, str]:
    return str(module_name(val)), demangle(module_local_name(val))


def class_method(fun: lf.Expr, pattern: re.Pattern[str]) -> str | None:
    """Return the operator of `fun` if it is a class method matching `pattern`, or None.

    Accepts the class methods of `GHC.Classes` and the instance methods (`$c==15`,
    `$c>=1`) that damlc generates in any module.
    """
    fun = untyped(fun)
    if fun.val is None:
        return None
    module, name = qual_name(fun.val)
    if module != EQ_MODULE and not name.startswith("$c"):
        return None
    match = pattern.match(name)
    return match[1] if match else None


def eq_operator(fun: lf.Expr) -> str | None:
    """Return `==` or `/=` if `fun` is an equality test (builtin or `Eq` method), or None."""
    fun = untyped(fun)
    if fun.builtin is not None:
        return "==" if lf_name(fun.builtin) == "EQUAL" else None
    return class_method(fun, EQ_RE)


def order_name(fun: lf.Expr) -> str | None:
    """Return `<`, `<=`, `>` or `>=` if `fun` is an ordering test (builtin or `Ord` method)."""
    fun = untyped(fun)
    if fun.builtin is not None:
        return ORDERS.get(lf_name(fun.builtin))
    return class_method(fun, ORDER_RE)


def abs_name(fun: lf.Expr) -> str | None:
    """Return `abs` if `fun` is the `abs` method of `Num`, or None."""
    fun = untyped(fun)
    if fun.val is None:
        return None
    module, name = qual_name(fun.val)
    if module == NUM_MODULE and ABS_RE.match(name):
        return "abs"
    return None


def arith_name(fun: lf.Expr) -> str | None:
    """Return `*` or `/` if `fun` multiplies or divides (builtin or `Num` method), or None."""
    fun = untyped(fun)
    if fun.builtin is not None:
        return ARITH.get(lf_name(fun.builtin))
    if fun.val is None:
        return None
    module, name = qual_name(fun.val)
    if module != NUM_MODULE:
        return None
    match = ARITH_RE.match(name)
    return match[1] if match else None


def numeric_lit(expr: lf.Expr) -> str | None:
    """Return a non-zero `Decimal` literal as text (`0.0001`), or None."""
    if expr.prim_lit is None or expr.prim_lit.numeric is None:
        return None
    value = Decimal(expr.prim_lit.numeric)
    if value == 0:
        return None
    return format(value.normalize(), "f")


def is_time(typ: lf.Type) -> bool:
    """Return True if `typ` is `Time`."""
    return typ.prim is not None and typ.prim.prim == lf.PrimType.TIMESTAMP


def reads_time(name: lf.ValName) -> bool:
    """Return True if value `name` reads the ledger time (`getTime`, `isLedgerTimeLT`, ...)."""
    return qual_name(name) in TIME_READS


def compare_name(fun: lf.Expr) -> str | None:
    """Return the comparison `fun` performs (`==`, `/=`, `elem`, `notElem`), or None."""
    operator = eq_operator(fun)
    if operator is not None:
        return operator
    fun = untyped(fun)
    if fun.val is not None and qual_name(fun.val) in MEMBERSHIP:
        module, name = qual_name(fun.val)
        return name
    return None


def is_compare(fun: lf.Expr) -> bool:
    """Return True if `fun` is an equality or membership test."""
    return compare_name(fun) is not None


def partial_name(fun: lf.Expr) -> str | None:
    """Return the name of the partial library function `fun` refers to (`head`, ...), or None."""
    fun = untyped(fun)
    if fun.val is None:
        return None
    module, name = qual_name(fun.val)
    if (module, name) in PARTIAL:
        return name
    return None
