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
| [`unused-template-field`](#unused-template-field) | Informational | Medium | Template field that no ledger code reads |
| [`hardcoded-party`](#hardcoded-party) | Medium | High | Party identity built from or compared with a text literal |
| [`partial-function`](#partial-function) | Low | Medium | Choice argument passed to `head`, `fromSome`, `!!`, ... |
| [`discarded-update`](#discarded-update) | Medium | High | Ledger actions wrapped in `pure` and never run |

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
`let` aliases, and records which argument fields reach the controllers and
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
$ damlisk scan examples/vulnerable/missing-amount-check/missing-amount-check.dar --detect missing-amount-check
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

### unused-template-field

**Unused template field** (Slither `unused-state`). It reports template fields that no
`ensure`, signatory, observer, key, choice, interface view or helper ever reads.

**Impact:** an unused field is stored and disclosed to every stakeholder on every contract, but
the ledger never enforces anything with it. Often it is just leftover data; sometimes it is a
check that was planned and never written, which is worse because the field suggests a rule
that does not exist.

| Field | Reported | Why |
|---|---|---|
| `acceptedToken : Text`, never compared | yes | stored, never enforced |
| `owner` used in `observer owner` | no | read by the observer clause |
| `note` returned by `pure note` | no | read by a choice |
| `limit.cap` read after `fetch limitCid` | no | read through a fetched contract |

**Example** (`examples/vulnerable/unused-template-field/daml/Main.daml`):

```haskell
template Campaign
  with
    platform : Party
    owner : Party
    target : Decimal
    acceptedToken : Text
    note : Text
  where
    signatory platform
    observer owner
    ensure target > 0.0

    choice Invest : ContractId Campaign
      with
        investor : Party
        token : Text
        amount : Decimal
        limitCid : ContractId Limit
      controller investor, platform
      do
        limit <- fetch limitCid
        assertMsg "over cap" (amount <= limit.cap)
        create this with target = target - amount
```

`Invest` never compares `token` with `acceptedToken`, so the campaign accepts any token.

```
$ damlisk scan examples/vulnerable/unused-template-field/unused-template-field.dar --detect unused-template-field
[Informational] unused-template-field Main.daml:11
    Main:Campaign: no code reads `acceptedToken`
1 finding(s).
```

**How it works:** the detector collects every record projection (`x.field`) in user code,
plus the projections inside the `$sel:` / `GetField` getters that user code calls (dot syntax
on a fetched contract may compile to a getter). Derived code is skipped because it touches every
field mechanically: `Show`, `Eq` and `Ord` instances, setters and the `$W` constructor wrapper.

**Results on real code:**

- `splice-amulet-0.1.24`: 7 templates, for example `ValidatorRight.dso` (neither signatory
  nor observer) and `ValidatorLicense.sponsor` (documented in Splice as deprecated).
- `splice-wallet-payments-0.1.24`: `reference` of the two `Terminated*` templates.

**Why Medium confidence:** off-ledger applications may read the field through codegen (for
example audit or display data such as `reason`), and fields read only by other packages are not
visible in this DAR.

**Recommendation:** enforce the field where it matters or remove it.

### hardcoded-party

**Hardcoded party.** damlc rejects party literals, but a party can still be pinned in code by
converting text. The detector reports:

1. `partyFromText` (or the `TEXT_TO_PARTY` builtin) applied to an expression that contains a
   text literal, including obfuscated ones such as `partyFromText (T.reverse "0221::nedduH")`
   or a custom decoder over an encoded string;
2. `partyToText x` compared (`==`, `/=`, `elem`, `notElem`) with a text literal.

**Impact:** a hardcoded party is invisible to the people who sign the contract. Used as an
observer it discloses every contract to a third party; used as a beneficiary it diverts value;
used in a comparison it grants authority to whoever owns that party id, on every deployment.
Party ids also differ between environments, so the code silently breaks or misroutes when
promoted.

| Code | Reported | Why |
|---|---|---|
| `fromSome (partyFromText "Operator::1220aa")` | yes | party from a literal |
| `fromSome (partyFromText (T.reverse "0221::nedduH"))` | yes | obfuscated literal |
| `partyToText actor == "Admin::1220bb"` | yes | authority decided by a literal |
| `fromSome (partyFromText name)` with `name` a choice argument | no | parsed from input |
| `partyToText owner <> " holds "` | no | formatting, not a comparison |

**Example** (`examples/vulnerable/hardcoded-party/daml/Main.daml`):

```haskell
operator : Party
operator = fromSome (partyFromText "Operator::1220aa")

hidden : Party
hidden = fromSome (partyFromText (T.reverse "0221::nedduH"))

template Vault
  with
    owner : Party
    amount : Decimal
  where
    signatory owner
    observer operator, hidden
```

```
$ damlisk scan examples/vulnerable/hardcoded-party/hardcoded-party.dar --detect hardcoded-party
[Medium] hardcoded-party Main.daml:21
    Main:Vault.Withdraw.update: party compared with text literal "Admin::1220bb"
[Medium] hardcoded-party Main.daml:10
    Main:hidden: party built from text literal "0221::nedduH"
[Medium] hardcoded-party Main.daml:7
    Main:operator: party built from text literal "Operator::1220aa"
3 finding(s).
```

**Results on real code:** `splice-token-standard-utils-2.0.0` reports
`specialAccountOwnerStubV1 = partyFromText "cip-112_no-owner::1220000..."`, the CIP-112
placeholder owner (intended, but a genuine hardcoded party). The rest of Splice is clean:
`partiesFromMeta` parses parties from metadata at runtime and is not reported.

**Recommendation:** pass parties in as template fields or choice arguments and check them
against signatories; never derive disclosure or authority from text.

### partial-function

**Partial function on a choice argument.** It reports template choices that pass data from
their argument to a partial library function: `head`, `tail`, `last`, `init`, `!!`, `foldl1`,
`foldr1` (`DA.List`), `maximum`, `minimum` (`DA.Foldable`), `fromSome` (`DA.Optional`),
`fromJust` (`DA.Maybe`), `fromLeft`, `fromRight` (`DA.Either`).

**Impact:** an empty list or `None` aborts the whole transaction with a generic error. When
the input comes from the caller, whoever submits the choice (or the workflow feeding it) can
make it fail on purpose, blocking a settlement or a payout that other contracts depend on.

| Code | Reported | Why |
|---|---|---|
| `choice Payout with winners : [Party]` ... `head winners` | yes | caller controls the list |
| `fromSome price` with `price : Optional Decimal` argument | yes | caller controls the optional |
| `head members` with `members` a template field | no | contract state, validated at creation |
| `fromSomeNote "no price" price` | no | explicit, intended failure |
| `DA.List.Total.head` | no | total version |

**Example** (`examples/vulnerable/partial-function/daml/Main.daml`):

```haskell
    choice Payout : Party
      with
        winners : [Party]
      controller operator
      do pure (head winners)
```

```
$ damlisk scan examples/vulnerable/partial-function/partial-function.dar --detect partial-function
[Low] partial-function Main.daml:27
    Main:Pool.Latest: argument reaches partial function: `batch` -> last
[Low] partial-function Main.daml:15
    Main:Pool.Payout: argument reaches partial function: `winners` -> head
[Low] partial-function Main.daml:21
    Main:Pool.Settle: argument reaches partial function: `price` -> fromSome
3 finding(s).
```

**How it works:** the same field-flow analysis as `controller-from-argument` follows the
argument through compiler helpers and `let` bindings, and records which fields reach a call
that resolves to one of the functions above. Results of ledger operations bound in `do`
(`x <- fetch …`, `x <- exercise …`) are ledger state, not caller input, so they do not carry
the argument further.

**Results on real code:** Splice and the `daml-contracts` DARs are clean: Splice uses
`fromSomeNote` and explicit checks, and the `head` calls in `fundraising` operate on contract
state, not on choice arguments.

**Why Medium confidence:** a field counts as reaching the function if it appears anywhere in the
call's arguments (for example inside a filter predicate), even when the list itself does not
come from the argument.

**Recommendation:** pattern match on the input, use `fromSomeNote` / `DA.List.Total`, or add an
explicit `assertMsg` so the failure is intended and explained.

### discarded-update

**Discarded update.** It reports a `do` block that binds `pure x`, where `x` holds ledger
actions (its type contains `Update`, e.g. `[Update ()]`), and never uses the result.

**Impact:** the actions are built as values but never run. The choice commits successfully and
the caller believes the archives, creates or exercises happened. A `BurnAll` that burns nothing,
or a payout that pays nobody, leaves the ledger inconsistent with what off-ledger systems record.
damlc accepts this without a warning.

How damlc handles the common mistakes with folds and maps (verified with SDK 3.4.8):

| Code | Compiler | Runtime | Reported |
|---|---|---|---|
| `foldlA (\acc cid -> do c <- fetch cid; …) 0.0 cids` | ok | correct | no |
| `foldl (\acc cid -> do c <- fetch cid; …) 0.0 cids` | **type error** | – | – |
| `foldl (\acc cid -> acc >> archive cid) (pure ()) cids` | ok | correct, all archived | no |
| `_ <- pure (map archive cids)` | ok, no warning | **nothing archived** | **yes** |
| `_ <- pure (forA_ cids archive)` | ok, no warning | **nothing archived** | **yes** |
| `actions <- pure (map archive cids); sequence_ actions` | ok | correct | no |
| `let _ = map archive cids` | ok, no warning | **nothing archived** | no: damlc deletes the unused `let`, so the DAR has no trace of it |

**Example** (`examples/vulnerable/discarded-update/daml/Main.daml`):

```haskell
    nonconsuming choice BurnAll : ()
      with
        cids : [ContractId Coin]
      controller owner
      do
        _ <- pure (map archive cids)
        pure ()
```

```
$ damlisk scan examples/vulnerable/discarded-update/discarded-update.dar --detect discarded-update
[Medium] discarded-update Main.daml:19
    Main:Wallet.BurnAll.update: ledger actions wrapped in `pure` are never run
[Medium] discarded-update Main.daml:27
    Main:Wallet.BurnEach.update: ledger actions wrapped in `pure` are never run
2 finding(s).
```

**How it works:** Daml-LF keeps the result type of every `pure`. The detector looks for a
binding in a `do` / `let` block whose value is `pure x` with a type that mentions `Update`, and
whose binder is not used by any later statement.

**Results on real code:** Splice and the `daml-contracts` DARs are clean.

**Recommendation:** run the actions (`forA_ cids archive`, `mapA_ archive cids`,
`sequence_ (map archive cids)`), and use `foldlA` / `forA` instead of `foldl` / `map` when the
step is an `Update`.
