import re
from enum import Enum

from dazl.damlast import daml_lf_1 as lf

BOOLS = {lf.PrimCon.CON_TRUE: "True", lf.PrimCon.CON_FALSE: "False"}
ESCAPE_RE = re.compile(r"\$(?:\$|u([0-9a-f]{4}))")


def lf_name(value: object) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, Enum):
        return value.name
    return str(value)


def bool_const(expr: lf.Expr) -> str | None:
    return BOOLS.get(expr._Sum_value) if expr._Sum_name == "prim_con" else None


def demangle(name: str) -> str:
    return ESCAPE_RE.sub(lambda m: chr(int(m[1], 16)) if m[1] else "$", name)
