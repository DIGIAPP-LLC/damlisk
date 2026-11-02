# damlisk

Static analyzer for Daml contracts, in the spirit of Slither. It reads the Daml-LF of a `.dar`
(via [dazl](https://github.com/digital-asset/dazl-client)), walks every template, choice and
value, and runs detectors over it.

## Usage

```bash
make dev-init
damlisk scan path/to/project.dar
damlisk scan path/to/project.dar --json --fail-on medium
damlisk info path/to/project.dar
damlisk list-detectors
```

## Detectors

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`boolean-cst`](#boolean-cst) | Medium | Medium | Boolean constants used as conditions |
| [`boolean-equal`](#boolean-equal) | Informational | High | Comparison to `True` / `False` |
| [`controller-from-argument`](#controller-from-argument) | High | Medium | Consuming choice controlled only by an unchecked argument party |
| [`missing-amount-check`](#missing-amount-check) | Low | Medium | `Decimal` template field not constrained by `ensure` |

### boolean-cst

**Misuse of a Boolean constant.** It reports a `True`/`False` constant used where a real
condition is expected, and conditionals that only return constants. damlc compiles these
without a warning, so they reach the ledger unchanged.

| Pattern | Runtime behaviour | Impact |
|---|---|---|
| `if True` / `if False` | One branch never runs | The check or logic in the dead branch silently does nothing |
| `check \|\| True` | The condition always passes | `assertMsg`, `ensure` or a controller check validates nothing: authorization or balance bypass |
| `check && False` | The condition always fails | The choice always aborts, so the contract can never be archived through it: locked assets, denial of service |
| `if c then True else False` / `if c then False else True` | Correct but redundant | Often hides a wrong or inverted condition |

**Example** (`examples/vulnerable/boolean-cst/daml/Main.daml`):

```haskell
choice Deposit : ContractId Vault
  with
    value : Decimal
    check : Bool
  controller owner
  do
    assertMsg "positive" (check || True)
    create this with amount = amount + value

choice Close : ()
  with
    check : Bool
  controller owner
  do
    assertMsg "closed" (check && False)
```

`Deposit` accepts any value, because the guard is always true. `Close` can never succeed, so
the owner can never close the vault.

```
$ damlisk scan examples/vulnerable/boolean-cst/boolean-cst.dar --detect boolean-cst
[Medium] boolean-cst Main.daml:29
    Main:Vault.Close.update: result is always False regardless of the condition
[Medium] boolean-cst Main.daml:20
    Main:Vault.Deposit.update: result is always True regardless of the condition
[Medium] boolean-cst Main.daml:36
    Main:Vault.Touch.update: conditional returns its own condition (if c then True else False)
[Medium] boolean-cst Main.daml:10
    Main:Vault.Withdraw.update: condition is always True
4 finding(s).
```

**Why Medium:** the actual effect depends on what the condition guards. It can be a harmless
leftover or a full bypass, and the detector cannot tell whether the constant was intended.

**Recommendation:** remove the constant and use the intended condition. Replace
`if c then True else False` with `c`, and `if c then False else True` with `not c`.

**Limitations:** Daml-LF 2.1 drops expression locations, so the reported line is the line of the
enclosing `choice` declaration, recovered from the sources embedded in the DAR.

### boolean-equal

**Comparison to a Boolean constant.** It reports `==` and `/=` where one operand is `True` or
`False`. damlc compiles `x == True` to the `EQUAL` builtin and `x /= False` to the `Eq Bool`
instance method, both without a warning.

| Pattern | Simplifies to |
|---|---|
| `x == True`, `x /= False` | `x` |
| `x == False`, `x /= True` | `not x` |

**Impact:** no runtime effect, the result is the same. The risk is in review: double negations
such as `active /= False` or `True /= force` make an inverted guard easy to miss, and a mistyped
constant (`== False` instead of `== True`) silently flips who may exercise a choice.

**Example** (`examples/vulnerable/boolean-equal/daml/Main.daml`):

```haskell
template Ticket
  with
    issuer : Party
    holder : Party
    used : Bool
    valid : Bool
  where
    signatory issuer
    observer holder
    ensure valid == True

    choice Redeem : ContractId Ticket
      controller holder
      do
        assertMsg "already used" (used == False)
        create this with used = True
```

```
$ damlisk scan examples/vulnerable/boolean-equal/boolean-equal.dar --detect boolean-equal
[Informational] boolean-equal Main.daml:27
    Main:Ticket.Check.update: comparison with a Boolean constant (x /= False), use `x`
[Informational] boolean-equal Main.daml:14
    Main:Ticket.Redeem.update: comparison with a Boolean constant (x == False), use `not x`
[Informational] boolean-equal Main.daml:20
    Main:Ticket.Revoke.update: comparison with a Boolean constant (x /= True), use `not x`
[Informational] boolean-equal Main.daml:12
    Main:Ticket.precond: comparison with a Boolean constant (x == True), use `x`
4 finding(s).
```

**Recommendation:** use the Boolean directly: `ensure valid`, `assertMsg "already used" (not used)`.

**Limitations:** like `boolean-cst`, the reported line is the enclosing `choice` (or `ensure`)
line, because Daml-LF 2.1 drops expression locations.

### controller-from-argument

**Controller taken from the choice argument** (Slither `tx-origin`). It reports a consuming
template choice where:

1. every controller comes from a choice argument field (`controller requester`,
   `controller request.party`), with no contract party next to it;
2. the choice body never compares that field (`==`, `/=`, `elem`, `notElem`) against anything.

**Impact:** the ledger only checks that the controller authorized the exercise. If the
controller is whatever party the caller passes in, every party that can see the contract
(observers, parties it was divulged to) can exercise the choice as itself. Because the choice
is consuming, they can archive the contract and, with the signatories' authority, create a new
one, e.g. transfer an asset to themselves.

| Choice shape | Reported | Why |
|---|---|---|
| `controller requester` with no check | yes | anyone who sees the contract can exercise it |
| `controller request.party` with no check | yes | same, through a nested record |
| `controller owner, splitter` | no | `owner` must authorize too |
| `controller claimer` + `assertMsg "owner only" (claimer == owner)` | no | the argument is checked |
| `nonconsuming choice … controller viewer` | no | the contract is not archived; borrowed authority is covered by `delegated-authority-leak` |
| interface choice | no | the check belongs to the interface implementations |

**Example** (`examples/vulnerable/controller-from-argument/daml/Main.daml`):

```haskell
template Asset
  with
    issuer : Party
    owner : Party
    amount : Decimal
  where
    signatory issuer, owner

    choice Transfer : ContractId Asset
      with
        requester : Party
        newOwner : Party
      controller requester
      do create this with owner = newOwner
```

Any observer of `Asset` can exercise `Transfer` with `requester = itself` and
`newOwner = itself`, and the new contract is still signed by `issuer` and `owner`.

```
$ damlisk scan examples/vulnerable/controller-from-argument/controller-from-argument.dar --detect controller-from-argument
[High] controller-from-argument Main.daml:30
    Main:Asset.Approve: controlled by unchecked argument `request`
[High] controller-from-argument Main.daml:16
    Main:Asset.Transfer: controlled by unchecked argument `requester`
2 finding(s).
```

**How it works:** damlc moves controllers and choice bodies into generated helpers
(`$$sc_Asset_3 this arg`). The detector follows the choice argument through those helpers,
`let` aliases and `do` bindings, and records which argument fields reach the controllers and
which reach a comparison.

**Splice:** Splice uses argument controllers often, but the consuming ones either add a contract
party as co-controller (`controller sender, walletProvider`) or check the argument
(``require … (p `elem` [receiver, provider])``), so nothing is reported.

**Why Medium confidence:** any comparison of the argument counts as a check, even one that does
not restrict who may exercise (for example `requester /= newOwner`). A check done another way,
such as fetching a contract that has the argument party as signatory, is not recognised.

**Recommendation:** control the choice by a contract party (`controller owner`), add a contract
party as co-controller, or check the argument against the contract
(`assertMsg "owner only" (requester == owner)`).

### missing-amount-check

**Amount not checked by ensure** (Slither `missing-zero-check`). It reports `Decimal` /
`Numeric` template fields that the template's `ensure` clause never mentions.

**Impact:** `ensure` is the only invariant the ledger enforces on every create. Without it, a
signatory can create the contract with `amount = 0.0` or `amount = -100.0`. Every choice that
adds, subtracts or pays out that amount then has to defend itself, and one that forgets is
exploitable (negative transfers, inflated balances, division by zero).

| Template | Reported | Why |
|---|---|---|
| `amount : Decimal`, no `ensure` | yes | nothing constrains the amount |
| `ensure quantity > 0.0` with another field `price : Decimal` | yes, `price` | `price` is not mentioned |
| `ensure principal > 0.0` | no | checked |
| `ensure validAmount balance` | no | checked through a helper function |
| `count : Int` only | no | `Int` fields are mostly counters and nonces, not amounts |

**Example** (`examples/vulnerable/missing-amount-check/daml/Main.daml`):

```haskell
template Iou
  with
    issuer : Party
    owner : Party
    amount : Decimal
  where
    signatory issuer
    observer owner
```

```
$ damlisk scan examples/vulnerable/missing-amount-check/missing-amount-check.dar
[Low] missing-amount-check Main.daml:6
    Main:Iou: ensure does not check `amount`
[Low] missing-amount-check Main.daml:15
    Main:Order: ensure does not check `price`
2 finding(s).
```

**How it works:** damlc compiles `ensure` to `case $censure this of True -> ... ; False -> error`.
The detector traces only the condition (`$censure this`), follows it into the helper, and lists
the numeric fields of `this` that never appear there. The `False` branch is skipped because its
error message `show`s the whole contract.

**Splice:** it reports 6 templates in `splice-amulet-0.1.24` (for example
`TransferCommand.amount`, `OpenMiningRound.amuletPrice`, the `issuancePer*` fields of mining
rounds) and 2 in `splice-wallet-payments-0.1.24` (`targetAmount`). These are real gaps in the
`ensure` clauses; Splice validates those values in the choices that use them and the contracts
are created by the DSO or by the paying party, so the risk is low.

**Why Medium confidence:** a field mentioned in `ensure` counts as checked even if the
condition does not bound it (for example `ensure amount == amount`). Amounts inside nested
records (`payData.paymentAmount`) are not inspected.

**Recommendation:** constrain every amount in `ensure`, e.g. `ensure amount > 0.0`.
