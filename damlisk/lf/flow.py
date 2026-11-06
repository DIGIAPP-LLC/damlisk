from collections.abc import Callable
from dataclasses import dataclass, field

from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.builtins import compare_name, order_name, partial_name, untyped
from damlisk.lf.tree import child_terms, find_all, used_later

WHOLE = frozenset({"*"})
THIS = "@this"
Aliases = dict[str, frozenset[str]]
Visited = frozenset[lf.ValName]
Node = lf.Expr | lf.Update
Probe = Callable[[lf.Expr], str | None]


@dataclass(frozen=True)
class PartialUse:
    field: str
    function: str


@dataclass
class Usage:
    fields: set[str] = field(default_factory=set)
    compared: set[str] = field(default_factory=set)
    partial: set[PartialUse] = field(default_factory=set)
    fetched: set[str] = field(default_factory=set)
    linked: set[str] = field(default_factory=set)
    ordered: set[str] = field(default_factory=set)
    consumed: set[str] = field(default_factory=set)
    created: set[str] = field(default_factory=set)
    called: set[str] = field(default_factory=set)
    untrusted: set[str] = field(default_factory=set)

    def merge(self, other: "Usage") -> None:
        """Add everything `other` uses: fields, compared fields and partial-function uses."""
        self.fields |= other.fields
        self.add_sinks(other)

    def add_sinks(self, other: "Usage") -> None:
        """Add only the sinks of `other`: every field set except the plain `fields`."""
        self.compared |= other.compared
        self.partial |= other.partial
        self.fetched |= other.fetched
        self.linked |= other.linked
        self.ordered |= other.ordered
        self.consumed |= other.consumed
        self.created |= other.created
        self.called |= other.called
        self.untrusted |= other.untrusted


def exercised(update: lf.Update) -> lf.Expr | None:
    """Return the contract id that `update` exercises a choice on, or None."""
    if update.exercise is not None:
        return update.exercise.cid
    if update.exercise_interface is not None:
        return update.exercise_interface.cid
    if update.soft_exercise is not None:
        return update.soft_exercise.cid
    return None


def iface_cid(update: lf.Update) -> lf.Expr | None:
    """Return the contract id that `update` exercises or fetches through an interface, or None."""
    if update.exercise_interface is not None:
        return update.exercise_interface.cid
    if update.fetch_interface is not None:
        return update.fetch_interface.cid
    return None


def create_arg(update: lf.Update) -> lf.Expr | None:
    """Return the record that `update` creates a contract from, or None."""
    if update.create is not None:
        return update.create.expr
    if update.create_interface is not None:
        return update.create_interface.expr
    return None


def call_parts(update: lf.Update) -> list[lf.Expr]:
    """Return the contract id and the choice argument of an exercise, or [] for other actions."""
    if update.exercise is not None:
        return [update.exercise.cid, update.exercise.arg]
    if update.exercise_interface is not None:
        return [update.exercise_interface.cid, update.exercise_interface.arg]
    if update.soft_exercise is not None:
        return [update.soft_exercise.cid, update.soft_exercise.arg]
    return []


def peel(expr: lf.Expr) -> lf.Expr:
    """Return the body of `expr` under all its lambdas."""
    while expr.abs is not None:
        expr = expr.abs.body
    return expr


def linked_fields(args: list[Usage]) -> set[str]:
    """Return the fields that a comparison checks against another tracked value.

    `tok.issuer == issuer` links `tok` to the contract (`THIS`); `tok.status == Done` only
    compares with a constant and links nothing.
    """
    mixed: set[str] = set()
    for arg in args:
        mixed |= arg.fields
    if len(mixed) < 2:
        return set()
    return mixed - {THIS}


@dataclass(frozen=True)
class Helper:
    name: lf.ValName | None
    body: lf.Expr

    def params(self, count: int) -> list[str]:
        """Return the names of the first `count` lambda parameters of the helper body."""
        names: list[str] = []
        lambdas = find_all(self.body, lf.Expr.Abs)
        for lam in lambdas:
            names.extend(param.var for param in lam.node.param)
        return names[:count]

    def visited(self, visited: Visited) -> Visited:
        """Return `visited` extended with this helper, so recursive helpers stop."""
        return visited | {self.name} if self.name else visited


class FieldFlow:
    def __init__(self, values: dict[lf.ValName, lf.DefValue]) -> None:
        """Remember all package values, so calls to compiler helpers can be followed."""
        self.values = values

    def fields(self, expr: lf.Expr, var: str) -> set[str]:
        """Return the fields of record variable `var` that `expr` uses."""
        return self.trace(expr, {var: WHOLE}).fields

    def compared(self, expr: lf.Expr, var: str) -> set[str]:
        """Return the fields of `var` that reach `==`, `/=`, `elem` or `notElem` in `expr`."""
        return self.trace(expr, {var: WHOLE}).compared

    def partial(self, expr: lf.Expr, var: str) -> set[PartialUse]:
        """Return the fields of `var` that reach a partial function such as `head` in `expr`."""
        return self.trace(expr, {var: WHOLE}).partial

    def ordered(self, expr: lf.Expr, var: str) -> set[str]:
        """Return the fields of `var` that reach `<`, `<=`, `>` or `>=` in `expr`."""
        return self.trace(expr, {var: WHOLE}).ordered

    def consumed(self, expr: lf.Expr, var: str) -> set[str]:
        """Return the contract-id fields of `var` that `expr` exercises a choice on (`archive`)."""
        return self.trace(expr, {var: WHOLE}).consumed

    def created(self, expr: lf.Expr, var: str) -> set[str]:
        """Return the fields of `var` that reach a created record in `expr`."""
        return self.trace(expr, {var: WHOLE}).created

    def called(self, expr: lf.Expr, var: str) -> set[str]:
        """Return the fields of `var` that reach an exercised contract id or choice argument."""
        return self.trace(expr, {var: WHOLE}).called

    def iface_cids(self, expr: lf.Expr, var: str) -> set[str]:
        """Return the fields of `var` that `expr` exercises or fetches through an interface."""
        return self.trace(expr, {var: WHOLE}).untrusted

    def fetch_usage(self, expr: lf.Expr, var: str, this: str) -> Usage:
        """Trace choice argument `var` and contract `this` through `expr`.

        `fetched` holds the contract-id fields of `var` whose fetched contract is read;
        `linked` holds the fields compared with a field of `this` or of another argument.
        """
        return self.trace(expr, {var: WHOLE, this: frozenset({THIS})})

    def trace(self, node: Node, aliases: Aliases, visited: Visited = frozenset()) -> Usage:
        """Return how `node` uses the fields carried by the variables in `aliases`."""
        if isinstance(node, lf.Update):
            if node.block is not None:
                return self.trace_block(node.block, aliases, visited, False)
            usage = self.trace_children(node, aliases, visited)
            cid = exercised(node)
            if cid is not None:
                usage.consumed |= self.trace(cid, aliases, visited).fields
            target = iface_cid(node)
            if target is not None:
                usage.untrusted |= self.trace(target, aliases, visited).fields
            record = create_arg(node)
            if record is not None:
                usage.created |= self.trace(record, aliases, visited).fields
            parts = call_parts(node)
            for part in parts:
                usage.called |= self.trace(part, aliases, visited).fields
            return usage
        if node.var is not None:
            return Usage(fields=set(aliases.get(node.var, ())))
        if node.rec_proj is not None:
            return self.trace_projection(node.rec_proj, aliases, visited)
        if node.let is not None:
            return self.trace_block(node.let, aliases, visited, True)
        if node.app is not None:
            return self.trace_call(node.app, aliases, visited)
        return self.trace_children(node, aliases, visited)

    def trace_children(self, node: Node, aliases: Aliases, visited: Visited) -> Usage:
        """Merge the usage of every direct sub-expression of `node`."""
        usage = Usage()
        children = child_terms(node)
        for child in children:
            usage.merge(self.trace(child, aliases, visited))
        return usage

    def trace_projection(self, proj: lf.Expr.RecProj, aliases: Aliases, visited: Visited) -> Usage:
        """Handle `record.field`: a projection of a tracked variable uses that field."""
        record = proj.record.var
        if record is None:
            return self.trace(proj.record, aliases, visited)
        labels = aliases.get(record, frozenset())
        if labels == WHOLE:
            return Usage(fields={proj.field})
        return Usage(fields=set(labels))

    def trace_block(self, block: lf.Block, aliases: Aliases, visited: Visited, pure: bool) -> Usage:
        """Handle `let` (pure) and `do` blocks.

        In a `let`, a binder bound to tracked fields becomes an alias of them. In a `do`
        block the binder holds the result of a ledger operation (exercise, create), which is
        ledger state rather than caller input, so it is not aliased. The one exception is
        `c <- fetch cid` on a tracked contract id that is read later: `c` becomes an alias of
        the id's fields, so checks on `c` count as checks on the id, and the id is recorded
        as fetched.
        """
        usage = Usage()
        scope = dict(aliases)
        for pos, binding in enumerate(block.bindings):
            bound = self.trace(binding.bound, scope, visited)
            usage.merge(bound)
            name = binding.binder.var
            if not bound.fields:
                continue
            if pure:
                scope[name] = frozenset(bound.fields)
            elif self.fetches(binding.bound) and used_later(block, pos, name):
                scope[name] = frozenset(bound.fields)
                usage.fetched |= bound.fields - {THIS}
        usage.merge(self.trace(block.body, scope, visited))
        return usage

    def trace_call(self, call: lf.Expr.App, aliases: Aliases, visited: Visited) -> Usage:
        """Handle a function call: record sinks, then follow the call into package helpers."""
        args = [self.trace(arg, aliases, visited) for arg in call.args]
        usage = Usage()
        comparison = self.resolve(call.fun, compare_name)
        partial = self.resolve(call.fun, partial_name)
        ordering = self.resolve(call.fun, order_name)
        for arg in args:
            usage.add_sinks(arg)
            if comparison is not None:
                usage.compared |= arg.fields
            if partial is not None:
                usage.partial |= {PartialUse(name, partial) for name in arg.fields}
            if ordering is not None:
                usage.ordered |= arg.fields
        if comparison is not None:
            usage.linked |= linked_fields(args)
        usage.merge(self.trace_callbacks(call, args, aliases, visited))
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

    def trace_callbacks(
        self, call: lf.Expr.App, args: list[Usage], aliases: Aliases, visited: Visited
    ) -> Usage:
        """Trace the functions passed to a higher-order call such as `forA cids (\\c -> ...)`.

        The first parameter of each callback stands for the elements of the other arguments,
        so `forA cids archive` uses `cids` the way `archive` uses its parameter.
        """
        usage = Usage()
        inputs: set[str] = set()
        callbacks: list[Helper] = []
        for pos, arg in enumerate(call.args):
            callback = self.callback(arg, visited)
            if callback is None:
                inputs |= args[pos].fields
            else:
                callbacks.append(callback)
        if not inputs:
            return usage
        for callback in callbacks:
            params = callback.params(1)
            if params:
                scope = dict(aliases)
                scope[params[0]] = frozenset(inputs)
                usage.merge(self.trace(callback.body, scope, callback.visited(visited)))
        return usage

    def callback(self, arg: lf.Expr, visited: Visited) -> Helper | None:
        """Return `arg` as a callback: a lambda, or a helper that runs a ledger action."""
        fun = untyped(arg)
        if fun.abs is not None:
            return Helper(None, fun)
        helper = self.helper(fun, visited)
        if helper is None or peel(helper.body).update is None:
            return None
        return helper

    def fetches(self, expr: lf.Expr) -> bool:
        """Return True if `expr` is `fetch cid`, written inline or as a call to a fetch helper.

        damlc compiles `fetch cid` to a call of a generated helper that only fetches.
        """
        if expr.app is not None:
            helper = self.helper(expr.app.fun, frozenset())
            if helper is None:
                return False
            expr = helper.body
        expr = peel(expr)
        return expr.update is not None and expr.update.fetch is not None

    def helper(self, fun: lf.Expr, visited: Visited) -> Helper | None:
        """Return the lambda or package value that `fun` calls, or None if it is opaque."""
        fun = untyped(fun)
        if fun.abs is not None:
            return Helper(None, fun)
        name = fun.val
        if name is None or name in visited or name not in self.values:
            return None
        return Helper(name, self.values[name].expr)

    def resolve(self, fun: lf.Expr, probe: Probe) -> str | None:
        """Return what `probe` finds for `fun`, looking through helpers that only alias it.

        damlc often wraps a library function in a generated value such as
        `$$sc_X_18 = elem @Party $fEqParty`; this follows such aliases.
        """
        seen: set[lf.ValName] = set()
        while True:
            found = probe(fun)
            if found is not None:
                return found
            name = untyped(fun).val
            if name is None or name in seen or name not in self.values:
                return None
            seen.add(name)
            body = self.values[name].expr
            fun = body.app.fun if body.app is not None else body

    def call_args(self, call: lf.Expr.App) -> list[lf.Expr]:
        """Return the arguments of `call`, including those fixed by a partially applied helper.

        damlc compiles `0.01 >= abs d` to `$$sc_X_14 (abs d)` with `$$sc_X_14 = (>=) 0.01`.
        """
        args = list(call.args)
        fun = untyped(call.fun)
        if fun.val is None or fun.val not in self.values:
            return args
        body = self.values[fun.val].expr
        if body.app is None:
            return args
        return list(body.app.args) + args
