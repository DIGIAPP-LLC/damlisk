import pytest
from dazl.damlast import daml_lf_1 as lf

from damlisk.lf.index import decl_re, known, value_re
from damlisk.lf.tree import find_all


def test_amulet_index_covers_all_packages(amulet_index):
    assert len(amulet_index.packages) == 51
    assert len(amulet_index.values) > 20000
    assert sum(len(v) for v in amulet_index.impls.values()) == 23
    assert any(str(name).endswith(":Splice.Amulet:Amulet") for name in amulet_index.templates)


def test_amulet_choice_values_are_attributed_to_choices(amulet_index):
    owners = {b.owner for b in amulet_index.bodies()}

    assert "Splice.AmuletRules:AmuletRules.AmuletRules_Transfer.update" in owners
    assert not any("$$$$sc_" in owner for owner in owners if ".update" in owner)


@pytest.mark.parametrize(
    "owner,attributed",
    [
        ("Main:fee", True),
        ("Main:Account.Deposit.update", True),
        ("Main:$$$$sc_fee_2", False),
        ("Main:$$$$sc_fee_1", False),
    ],
    ids=["named-value", "choice", "trace-helper", "math-helper"],
)
def test_helpers_are_attributed_to_named_values(trace_index, owner, attributed):
    owners = {b.owner for b in trace_index.bodies()}

    assert (owner in owners) is attributed


def test_index_resolves_values_referenced_by_choices(amulet_index):
    body = next(b for b in amulet_index.bodies() if b.owner.endswith("AmuletRules_Transfer.update"))
    names = [ref.node for ref in find_all(body.expr, lf.ValName)]

    assert names and all(n in amulet_index.values for n in names)


@pytest.mark.parametrize(
    "owner,line",
    [
        ("Main:Vault.Withdraw.update", 9),
        ("Main:Vault.Deposit.update", 19),
        ("Main:Vault.Close.update", 28),
        ("Main:Vault.Safe.update", 44),
        ("Main:Vault.signatories", 2),
    ],
)
def test_bool_choice_locations_come_from_sources(bool_index, owner, line):
    body = next(b for b in bool_index.bodies() if b.owner == owner)

    assert body.loc.range.start_line == line


@pytest.mark.parametrize(
    "pattern,text,matches",
    [
        (decl_re("choice", "Close"), "    choice Close : ()", True),
        (decl_re("choice", "Close"), "    nonconsuming choice Close : ()", True),
        (decl_re("choice", "Close"), "    choice CloseAll : ()", False),
        (decl_re("template", "Vault"), "template Vault", True),
        (value_re("transfer"), "transfer : Party -> Update ()", True),
        (value_re("transfer"), "  transfer = 1", False),
    ],
)
def test_source_patterns(pattern, text, matches):
    assert bool(pattern.match(text)) is matches


@pytest.mark.parametrize(
    "rng,expected",
    [((0, 0, 0, 0), False), ((3, 0, 3, 5), True), ((0, 2, 0, 9), True)],
    ids=["zero", "real", "first-line"],
)
def test_known_drops_empty_locations(rng, expected):
    loc = lf.Location(
        lf.ModuleRef(lf.PackageRef("p"), lf.DottedName(("M",))), lf.Location.Range(*rng)
    )

    assert (known(loc) is not None) is expected


@pytest.mark.parametrize(
    "choice,expected",
    [("Claim", ["now"]), ("Extend", ["newUnlock"]), ("SafeClaim", []), ("Archive", [])],
    ids=["one-field", "other-field", "unit-argument", "archive"],
)
def test_arg_fields(time_index, choice, expected):
    decls = {decl.choice.name: decl for decl in time_index.choices()}

    assert [field.field for field in time_index.arg_fields(decls[choice])] == expected


@pytest.mark.parametrize(
    "choice,minimum",
    [("Claim", 2), ("SafeClaim", 2), ("Reschedule", 2)],
    ids=["claim", "safe-claim", "reschedule"],
)
def test_reachable_follows_helpers(time_index, choice, minimum):
    decls = {decl.choice.name: decl for decl in time_index.choices()}
    root = decls[choice].choice.update
    bodies = time_index.reachable(root)

    assert bodies[0] is root
    assert len(bodies) >= minimum
    assert all(isinstance(body, lf.Expr) for body in bodies)
