from dataclasses import dataclass, field

from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.builtins import is_compare, untyped
from damlisk.lf.tree import child_terms, find_all

WHOLE = frozenset({"*"})
Aliases = dict[str, frozenset[str]]
Visited = frozenset[lf.ValName]
Node = lf.Expr | lf.Update


@dataclass
class Usage:
    fields: set[str] = field(default_factory=set)
    compared: set[str] = field(default_factory=set)

    def merge(self, other: "Usage") -> None:
        self.fields |= other.fields
        self.compared |= other.compared


@dataclass(frozen=True)
class Helper:
    name: lf.ValName | None
    body: lf.Expr

    def params(self, count: int) -> list[str]:
        names: list[str] = []
        lambdas = find_all(self.body, lf.Expr.Abs)
        for lam in lambdas:
            names.extend(param.var for param in lam.node.param)
        return names[:count]

    def visited(self, visited: Visited) -> Visited:
        return visited | {self.name} if self.name else visited


class FieldFlow:
    def __init__(self, values: dict[lf.ValName, lf.DefValue]) -> None:
        self.values = values

    def fields(self, expr: lf.Expr, var: str) -> set[str]:
        return self.trace(expr, {var: WHOLE}).fields

    def compared(self, expr: lf.Expr, var: str) -> set[str]:
        return self.trace(expr, {var: WHOLE}).compared

    def trace(self, node: Node, aliases: Aliases, visited: Visited = frozenset()) -> Usage:
        if isinstance(node, lf.Update):
            if node.block is not None:
                return self.trace_block(node.block, aliases, visited)
            return self.trace_children(node, aliases, visited)
        if node.var is not None:
            return Usage(fields=set(aliases.get(node.var, ())))
        if node.rec_proj is not None:
            return self.trace_projection(node.rec_proj, aliases, visited)
        if node.let is not None:
            return self.trace_block(node.let, aliases, visited)
        if node.app is not None:
            return self.trace_call(node.app, aliases, visited)
        return self.trace_children(node, aliases, visited)

    def trace_children(self, node: Node, aliases: Aliases, visited: Visited) -> Usage:
        usage = Usage()
        children = child_terms(node)
        for child in children:
            usage.merge(self.trace(child, aliases, visited))
        return usage

    def trace_projection(self, proj: lf.Expr.RecProj, aliases: Aliases, visited: Visited) -> Usage:
        record = proj.record.var
        if record is None:
            return self.trace(proj.record, aliases, visited)
        labels = aliases.get(record, frozenset())
        if labels == WHOLE:
            return Usage(fields={proj.field})
        return Usage(fields=set(labels))

    def trace_block(self, block: lf.Block, aliases: Aliases, visited: Visited) -> Usage:
        usage = Usage()
        scope = dict(aliases)
        for binding in block.bindings:
            bound = self.trace(binding.bound, scope, visited)
            usage.merge(bound)
            if bound.fields:
                scope[binding.binder.var] = frozenset(bound.fields)
        usage.merge(self.trace(block.body, scope, visited))
        return usage

    def trace_call(self, call: lf.Expr.App, aliases: Aliases, visited: Visited) -> Usage:
        args = [self.trace(arg, aliases, visited) for arg in call.args]
        usage = Usage()
        compares = self.is_comparison(call.fun)
        for arg in args:
            usage.compared |= arg.compared
            if compares:
                usage.compared |= arg.fields
        helper = self.helper(call.fun, visited)
        if helper is None:
            usage.merge(self.trace(call.fun, aliases, visited))
            for arg in args:
                usage.fields |= arg.fields
            return usage
        params = helper.params(len(args))
        inner: Aliases = {}
        for pos, arg in enumerate(args):
            if pos >= len(params):
                usage.fields |= arg.fields
            elif arg.fields:
                inner[params[pos]] = frozenset(arg.fields)
        if inner:
            usage.merge(self.trace(helper.body, inner, helper.visited(visited)))
        return usage

    def helper(self, fun: lf.Expr, visited: Visited) -> Helper | None:
        fun = untyped(fun)
        if fun.abs is not None:
            return Helper(None, fun)
        name = fun.val
        if name is None or name in visited or name not in self.values:
            return None
        return Helper(name, self.values[name].expr)

    def is_comparison(self, fun: lf.Expr) -> bool:
        seen: set[lf.ValName] = set()
        while not is_compare(fun):
            name = untyped(fun).val
            if name is None or name in seen or name not in self.values:
                return False
            seen.add(name)
            body = self.values[name].expr
            fun = body.app.fun if body.app is not None else body
        return True
