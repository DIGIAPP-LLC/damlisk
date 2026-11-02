import re
from enum import Enum

from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.util import module_local_name, module_name

BOOLS = {lf.PrimCon.CON_TRUE: "True", lf.PrimCon.CON_FALSE: "False"}
ESCAPE_RE = re.compile(r"\$(?:\$|u([0-9a-f]{4}))")
EQ_RE = re.compile(r"^(?:\$c|\$dm)?(==|/=)\d*$")
EQ_MODULE = "GHC.Classes"
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
    while fun.ty_app is not None:
        fun = fun.ty_app.expr
    return fun


def qual_name(val: lf.ValName) -> tuple[str, str]:
    return str(module_name(val)), demangle(module_local_name(val))


def eq_operator(fun: lf.Expr) -> str | None:
    fun = untyped(fun)
    if fun.builtin is not None:
        return "==" if lf_name(fun.builtin) == "EQUAL" else None
    if fun.val is None:
        return None
    module, name = qual_name(fun.val)
    if module != EQ_MODULE:
        return None
    match = EQ_RE.match(name)
    return match[1] if match else None


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
