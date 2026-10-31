import re
from enum import Enum

from dazl.damlast import daml_lf_1 as lf
from dazl.damlast.util import module_local_name, module_name

BOOLS = {lf.PrimCon.CON_TRUE: "True", lf.PrimCon.CON_FALSE: "False"}
ESCAPE_RE = re.compile(r"\$(?:\$|u([0-9a-f]{4}))")
EQ_RE = re.compile(r"^(?:\$c|\$dm)?(==|/=)\d*$")
EQ_MODULE = "GHC.Classes"
MEMBERSHIP = {("DA.Internal.Prelude", "elem"), ("DA.Internal.Prelude", "notElem")}


def lf_name(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Enum):
        return value.name
    return str(value)


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


def is_member(fun: lf.Expr) -> bool:
    fun = untyped(fun)
    return fun.val is not None and qual_name(fun.val) in MEMBERSHIP


def is_compare(fun: lf.Expr) -> bool:
    return is_member(fun) or eq_operator(fun) is not None
