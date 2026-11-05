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
| [`nonconsuming-create`](#nonconsuming-create) | High | Medium | Nonconsuming choice creates its own template without archiving `self` |
| [`unchecked-fetch`](#unchecked-fetch) | High | Medium | Contract fetched from a choice argument and used without validation |
| [`time-from-argument`](#time-from-argument) | Medium | Medium | Deadline logic on a caller-supplied `Time` instead of ledger time |
| [`amount-tolerance`](#amount-tolerance) | Medium | High | `Decimal` amounts compared with `abs (a - b) < eps` instead of exactly |
| [`divide-before-multiply`](#divide-before-multiply) | Medium | Medium | Result of a division multiplied, compounding its rounding error |
| [`unconsumed-input`](#unconsumed-input) | High | Medium | Input contract of the same template read but not archived |
| [`aborting-choice`](#aborting-choice) | Informational | High | Choice whose body always aborts |
| [`hash-concat-collision`](#hash-concat-collision) | Medium | Medium | `sha256` of texts joined without a separator |
| [`time-equality`](#time-equality) | Medium | High | Ledger time compared with `==` or `/=` |
| [`tautological-compare`](#tautological-compare) | Medium | High | Value compared with itself (`payer == payer`) |
| [`unprotected-archive`](#unprotected-archive) | High | Medium | Consuming choice controlled by a non-signatory |
| [`missing-ensure`](#missing-ensure) | Medium | High | Template with amount or time fields and no or trivial `ensure` |
| [`over-disclosure`](#over-disclosure) | Medium | Medium | Choice observers taken from the choice argument |
| [`unsafe-primitive`](#unsafe-primitive) | High | High | Unchecked cast of a contract id, interface or `Any` value |
| [`debug-trace`](#debug-trace) | Informational | High | Debug trace left in production code |
| [`stuck-asset`](#stuck-asset) | Medium | Medium | Asset its owner cannot move: no owner-controlled consuming choice |
| [`sdk-version`](#sdk-version) | Informational | High | DAR built for a Daml-LF 1.x target |
| [`rtlo`](#rtlo) | High | High | Bidirectional control character (right-to-left override) in source or `Text` |

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
| `currency : Text`, never compared | yes | stored, never enforced |
| `owner` used in `observer owner` | no | read by the observer clause |
| `note` returned by `pure note` | no | read by a choice |
| `limit.cap` read after `fetch limitCid` | no | read through a fetched contract |

**Example** (`examples/vulnerable/unused-template-field/daml/Main.daml`):

```haskell
template Shop
  with
    platform : Party
    owner : Party
    stock : Decimal
    currency : Text
    note : Text
  where
    signatory platform
    observer owner
    ensure stock > 0.0

    choice Buy : ContractId Shop
      with
        buyer : Party
        paid : Text
        amount : Decimal
        limitCid : ContractId Limit
      controller buyer, platform
      do
        limit <- fetch limitCid
        assertMsg "over cap" (amount <= limit.cap)
        create this with stock = stock - amount
```

`Buy` never compares `paid` with `currency`, so the shop accepts payment in any token.

```
$ damlisk scan examples/vulnerable/unused-template-field/unused-template-field.dar --detect unused-template-field
[Informational] unused-template-field Main.daml:11
    Main:Shop: no code reads `currency`
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

**Results on real code:** Splice is clean: it uses `fromSomeNote` and explicit checks.

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

**Results on real code:** Splice is clean.

**Recommendation:** run the actions (`forA_ cids archive`, `mapA_ archive cids`,
`sequence_ (map archive cids)`), and use `foldlA` / `forA` instead of `foldl` / `map` when the
step is an `Update`.

### nonconsuming-create

**Nonconsuming self-create.** It reports a `nonconsuming` choice that creates a contract of its
own template (`create this with …` or `create Token with …`) and never uses `self`, so nothing
archives the original contract.

**Impact:** the original stays active next to the new contracts, so the asset is duplicated.
The new contracts carry the authority of every signatory of the original: with
`signatory issuer, owner` and `controller owner`, the owner can mint tokens co-signed by the
issuer without the issuer taking part. A `Split` of 100 into 30 + 70 leaves the owner with 200.
damlc accepts this without a warning.

**Example** (`examples/vulnerable/nonconsuming-create/daml/Main.daml`):

```haskell
template Token
  with
    issuer : Party
    owner : Party
    amount : Decimal
  where
    signatory issuer, owner

    nonconsuming choice Split : (ContractId Token, ContractId Token)
      with
        part : Decimal
      controller owner
      do
        left <- create this with amount = part
        right <- create this with amount = amount - part
        pure (left, right)
```

```
$ damlisk scan examples/vulnerable/nonconsuming-create/nonconsuming-create.dar --detect nonconsuming-create
[High] nonconsuming-create Main.daml:21
    Main:Token.Copy: creates `Main:Token` but never archives `self`
[High] nonconsuming-create Main.daml:12
    Main:Token.Split: creates `Main:Token` but never archives `self`
2 finding(s).
```

`SafeSplit` (`archive self` first), `SafeMove` (`exercise self Archive`), the consuming `Merge`
and the read-only `Balance` are not reported.

**How it works:** damlc moves `create` into generated helpers (`$$sc_Token_4`), so the detector
follows every helper of the main package that the choice calls and collects the templates they
create. If the choice's own template is among them, it traces `self` through the same helpers;
any use of `self` (archive, exercise, passing it on) counts as handled.

**Results on real code:** Splice is clean: none of its nonconsuming choices creates its own
template.

**Recommendation:** make the choice consuming (the default), or call `archive self` before
creating the replacement contracts.

### unchecked-fetch

**Unchecked fetch.** It reports a choice that fetches a contract whose id comes from its
argument, reads the fetched data, and never compares that contract with the current contract or
with the other arguments.

**Impact:** `fetch` only proves that *some* contract of that template exists and is visible to
the submitter. Without a check such as `tok.issuer == trusted` or `tok.owner == borrower`, the
choice accepts a contract the caller created themselves, or one that belongs to someone else:
self-issued collateral, another user's balance, or the wrong account.

**Example** (`examples/vulnerable/unchecked-fetch/daml/Main.daml`):

```haskell
    nonconsuming choice Borrow : ContractId Debt
      with
        borrower : Party
        collateral : ContractId Token
      controller borrower
      do
        tok <- fetch collateral
        create Debt with bank, borrower, amount = tok.amount / 2.0
```

The borrower issues a `Token` to themselves for 1,000,000 and borrows 500,000 against it.

```
$ damlisk scan examples/vulnerable/unchecked-fetch/unchecked-fetch.dar --detect unchecked-fetch
[High] unchecked-fetch Main.daml:29
    Main:Bank.Borrow: fetched contract `collateral` is used without validation
[High] unchecked-fetch Main.daml:38
    Main:Bank.BorrowUsd: fetched contract `collateral` is used without validation
2 finding(s).
```

`BorrowUsd` is reported too: `tok.currency == "USD"` compares with a constant, which says
nothing about who issued the token. `SafeBorrow` (checks `tok.issuer == trusted` and
`tok.owner == borrower`) and `Exists` (fetches but never reads the data) are not reported.

**How it works:** the field-flow analysis treats `tok <- fetch cid` as an alias of the argument
field `cid` when `tok` is used later. A comparison (`==`, `/=`, `elem`, `notElem`, including
derived `Eq` instances) counts as a check only if it puts the fetched data next to a field of
`this` or of another argument. Fetches through library helpers that validate themselves, such
as Splice's `fetchChecked`, are not treated as raw fetches.

**Results on real code:** Splice is clean (it fetches through `fetchChecked` /
`fetchReferenceData`).

**Recommendation:** compare the fetched contract with trusted data before using it
(`assertMsg "issuer" (tok.issuer == trusted)`, matching ids or parties), or use a checked fetch
helper.

### time-from-argument

**Time from argument.** It reports a choice that compares a `Time` from its argument with `<`,
`<=`, `>` or `>=`, and never reads the ledger time: no `getTime`, `isLedgerTimeLT/LE/GT/GE`,
`assertWithinDeadline` or `assertDeadlineExceeded`, directly or in a helper of the package.

**Impact:** the controller decides what "now" is. Lock periods, vesting, claim windows,
expiry and default checks are not enforced: a `now` argument set in the future
expires a claim early, and one set in the past accepts it after its deadline.

**Example** (`examples/vulnerable/time-from-argument/daml/Main.daml`):

```haskell
    choice Claim : ()
      with
        now : Time
      controller owner
      do
        assertMsg "still locked" (now >= unlock)
```

```
$ damlisk scan examples/vulnerable/time-from-argument/time-from-argument.dar --detect time-from-argument
[Medium] time-from-argument Main.daml:14
    Main:Vesting.Claim: compares caller-supplied time `now`, not ledger time
[Medium] time-from-argument Main.daml:21
    Main:Vesting.Extend: compares caller-supplied time `newUnlock`, not ledger time
2 finding(s).
```

`Extend` (`newUnlock > unlock`) is reported too: without a clock check, a vesting that already
unlocked can be pushed back into the future. Splice's `TransferPreapproval_Renew` does the
same comparison but first calls `assertWithinDeadline`. `SafeClaim` (`getTime`), `BoundClaim`
(`assertDeadlineExceeded`) and `Reschedule` (stores the time without comparing it) are not
reported.

**How it works:** the argument record's field types come from the package's data types. The
field-flow analysis tracks the `Time` fields into ordering operators (builtins and `Ord`
instance methods such as `DA.Internal.LF:$c>=1`). The choice and every main-package helper it
reaches are then searched for a ledger-time read.

**Results on real code:** Splice is clean.

**Recommendation:** use `assertWithinDeadline` / `assertDeadlineExceeded` /
`isLedgerTimeLT` (they work with Canton's time bounds), or `now <- getTime`.

### amount-tolerance

**Amount tolerance.** It reports a comparison of an absolute value with a non-zero `Decimal`
literal, such as `abs (outputs - inputs) < 0.0001` or `0.01 >= abs (total - expected)`.

**Impact:** `Decimal` (`Numeric 10`) is exact fixed-point arithmetic, so a tolerance never
absorbs rounding noise: it only lets the two amounts differ by up to `eps`. A split, merge,
burn/mint or exchange that checks conservation this way can create up to `eps` tokens every
time, and the caller can repeat it as often as they like.

**Example** (`examples/vulnerable/amount-tolerance/daml/Main.daml`):

```haskell
    choice Split : [ContractId Token]
      with
        parts : [Decimal]
      controller owner
      do
        assertMsg "conserved" (abs (sum parts - amount) < 0.0001)
        forA parts $ \part -> create this with amount = part
```

```
$ damlisk scan examples/vulnerable/amount-tolerance/amount-tolerance.dar --detect amount-tolerance
[Medium] amount-tolerance Main.daml:19
    Main:Token.Merge.update: amounts compared with tolerance 0.01, not exactly
[Medium] amount-tolerance Main.daml:11
    Main:Token.Split.update: amounts compared with tolerance 0.0001, not exactly
2 finding(s).
```

`SafeSplit` (`sum parts == amount`) and `Grow` (`abs delta > 0.0`, a zero literal is an exact
sign check) are not reported.

**How it works:** every call to an ordering operator is checked for an argument that calls
`GHC.Num` `abs` and an argument that is a non-zero `Decimal` literal. damlc wraps `abs` in
generated aliases (`$$sc_X_13 = $cabs1 @10 ...`) and turns `0.01 >= x` into a partially
applied helper (`$$sc_X_14 = (>=) 0.01`); both are followed.

**Results on real code:** Splice is clean.

**Recommendation:** compare amounts exactly (`sum outputs == sum inputs`). When a division
leaves a remainder, assign it explicitly, e.g. to the last output or back to the sender.

### divide-before-multiply

**Divide before multiply.** It reports a multiplication whose operand is the result of a
division, written inline (`a / b * c`) or through a `let` (`let share = a / b in c * share`).

**Impact:** `Decimal` division rounds to 10 decimal places (`Int` division truncates), and the
multiplication then scales that rounding error. Payouts, fees and shares come out wrong;
summed over many recipients they no longer add up to the total, which leaves dust behind or
breaks a later conservation check.

**Example** (`examples/vulnerable/divide-before-multiply/daml/Main.daml`):

```haskell
    nonconsuming choice Payout : Decimal
      with
        stake : Decimal
      controller admin
      do
        let share = stake / total
        pure (reward * share)
```

```
$ damlisk scan examples/vulnerable/divide-before-multiply/divide-before-multiply.dar --detect divide-before-multiply
[Medium] divide-before-multiply Main.daml:19
    Main:Pool.Fee.update: result of a division is multiplied
[Medium] divide-before-multiply Main.daml:11
    Main:Pool.Payout.update: result of a division is multiplied
2 finding(s).
```

`Fee` (`amount / 10000.0 * bps`) is reported too. `SafePayout` (`reward * stake / total`) and
`Scale` (multiplies, then divides) are not reported.

**How it works:** multiplication and division are recognised as builtins (`MUL_NUMERIC`,
`DIV_NUMERIC`, `MUL_INT64`, `DIV_INT64`) or `GHC.Num` methods (`$c*`, `$c/`), also through the
`$$sc` aliases damlc generates. `let` variables bound to a division are tracked within the
same body.

**Results on real code:** `splice-amulet` 0.1.24 has 5 findings, all intentional tokenomics
arithmetic: `ratePerRoundToRatePerDay`, `computeIssuanceTranche`,
`computeIssuingRoundParameters`, `computeSynchronizerFees` (`trafficAmount / 1e6 * price`) and
`AmuletRules_ConvertFeaturedAppActivityMarkers` (`amountUsd / amuletPrice`, then `* weight`).
Splice's own comments accept the rounding error (up to `0.5e-10` per unit). The other Splice
packages are clean.

**Why Medium confidence:** some divisions are exact (an `Int` converted to `Decimal` and divided
by `1e6`), and some code accepts the error on purpose, as Splice does.

**Recommendation:** multiply first and divide last (`reward * stake / total`), and assign any
remainder explicitly.

### unconsumed-input

**Unconsumed input.** It reports a choice that takes contract ids of its own template as
input (`other : ContractId Token` or `others : [ContractId Token]`), uses them, creates a new
contract of that template, and never archives or exercises a choice on the inputs.

**Impact:** the inputs stay active after their value went into the new contract, so the same
value is counted twice. A merge, consolidation or top-up becomes a mint: the owner feeds the
same input in again and again.

**Example** (`examples/vulnerable/unconsumed-input/daml/Main.daml`):

```haskell
    choice Merge : ContractId Token
      with
        other : ContractId Token
      controller owner
      do
        tok <- fetch other
        assertMsg "same owner" (tok.owner == owner)
        create this with amount = amount + tok.amount
```

```
$ damlisk scan examples/vulnerable/unconsumed-input/unconsumed-input.dar --detect unconsumed-input
[High] unconsumed-input Main.daml:12
    Main:Token.Merge: input `other` is read but never archived
[High] unconsumed-input Main.daml:21
    Main:Token.MergeAll: input `others` is read but never archived
2 finding(s).
```

`MergeAll` (`forA others fetch`) is reported too. `SafeMerge` (`archive other`),
`SafeMergeAll` (`archive cid` inside `forA`) and `Rebase` (`exercise ref Archive`) are not
reported.

**How it works:** the argument fields typed `ContractId T` or `[ContractId T]`, where `T` is
the choice's own template, are traced with the field-flow analysis. A field counts as consumed
when it reaches the contract id of an `exercise` (`archive` compiles to `exercise … Archive`).
Functions passed to `forA`, `mapA`, `map` and similar calls are followed with their parameter
bound to the list, so `forA_ others archive` and `forA others (\cid -> archive cid)` count.
The choice must also create its own template, directly or through a main-package helper.

**Results on real code:** Splice is clean.

**Why Medium confidence:** any exercise counts as consuming, including a nonconsuming one, and
an input used only as a reference (never added to the new contract) is still reported.

**Recommendation:** archive every input after reading it (`archive other`,
`forA_ others archive`), or exercise a consuming choice on it.

### aborting-choice

**Aborting choice.** It reports a choice whose body always fails: it unconditionally reaches
`error`, `abort`, `fail` or `throw`, directly or through a helper such as Splice's
`deprecatedChoice`.

**Impact:** the choice stays in the template's API and in generated client bindings, but
every exercise is rejected. A stub left as `error "TODO"` means the action it promises
(withdraw, cancel, expire) is impossible; a deprecated choice sends clients to a dead end
unless it is documented.

**Example** (`examples/vulnerable/aborting-choice/daml/Main.daml`):

```haskell
unsupported : Text -> Update a
unsupported name = abort (name <> " is not supported")

    choice Withdraw : ()
      controller owner
      do error "TODO"

    choice Close : ()
      controller owner
      do
        unsupported "Close"
        pure ()
```

```
$ damlisk scan examples/vulnerable/aborting-choice/aborting-choice.dar --detect aborting-choice
[Informational] aborting-choice Main.daml:18
    Main:Vault.Close: every exercise aborts
[Informational] aborting-choice Main.daml:14
    Main:Vault.Withdraw: every exercise aborts
2 finding(s).
```

`Drain` (`if limit < amount then abort … else pure ()`) and `Check` (`assertMsg`) can succeed
and are not reported.

**How it works:** an expression always aborts if it is a `throw` or the `ERROR` builtin, a call
of a value that always aborts (followed through every package, so `abort` → `fail` →
`error` → `throw` is recognised), a `let` whose body aborts, a `case` whose every branch
aborts, or a `do` block with a statement that aborts.

**Results on real code:** `splice-amulet` 0.1.24 has 9 findings, exactly its deprecated
choices: `Amulet_Expire`, `LockedAmulet_Unlock`, `LockedAmulet_OwnerExpireLock`,
`LockedAmulet_ExpireAmulet`, `AmuletRules_ComputeFees`, the three
`AmuletRules_*FutureAmuletConfigSchedule` choices (`deprecatedChoice`) and
`ValidatorLicense_ReceiveFaucetCoupon` (`error "… is deprecated …"`). 0.1.14 has 4. The
conditional `error` / `abort` calls elsewhere in Splice are not reported. Note that
`AmuletRules_ComputeFees` still declares `expectedDso`, documented as "must always be set",
although the choice can no longer run.

**Recommendation:** implement or remove the choice. If it is kept only for upgrade
compatibility, mark it deprecated in its documentation and name the replacement choice.

### hash-concat-collision

**Hash of joined texts.** It reports `sha256` / `keccak256` applied to texts glued with `<>`
or `implode` where two variable parts touch, with no literal separator between them.

**Impact:** `"ab" <> "c"` and `"a" <> "bc"` are the same text, so different inputs share one
hash. A commitment, secret or id built this way can be matched by inputs nobody committed
to: one voucher secret opens another voucher, or two requests get the same id.

**Example** (`examples/vulnerable/hash-concat-collision/daml/Main.daml`):

```haskell
    choice Redeem : ContractId Voucher
      with
        claimed : Text
      controller holder
      do
        assertMsg "bad code" (T.sha256 (code <> batch) == claimed)
        create this with digest = claimed

    choice Seal : ContractId Voucher
      controller issuer
      do
        create this with digest = T.sha256 (T.implode [code, batch])
```

```
$ damlisk scan examples/vulnerable/hash-concat-collision/hash-concat-collision.dar --detect hash-concat-collision
[Medium] hash-concat-collision Main.daml:47
    Main:Voucher.Commit.update: hashed text joins parts without a separator
[Medium] hash-concat-collision Main.daml:16
    Main:Voucher.Redeem.update: hashed text joins parts without a separator
[Medium] hash-concat-collision Main.daml:24
    Main:Voucher.Seal.update: hashed text joins parts without a separator
3 finding(s).
```

`Commit` hashes `let payload = code <> batch`. `SafeRedeem` (`code <> "|" <> batch`),
`SafeSeal` (`T.intercalate "|" [code, batch]`) and `Stamp` (`"voucher:" <> code`) are not
reported.

**How it works:** the hashed argument is split into parts through `APPEND_TEXT`,
`IMPLODE_TEXT` over a list literal, partially applied helpers such as
`$$sc_X_10 = (<>) "|"` and `let` variables. A finding needs two neighbouring parts that are
both non-literal.

**Results on real code:** Splice is clean. `Splice.Amulet.CryptoHash` hashes
`intercalate "|" (show (length ts) :: ts)`: the parts are separated and length-prefixed,
and the elements are themselves hex digests that cannot contain `|`.

**Recommendation:** put a separator that cannot occur in the parts between them
(`intercalate "|"`), or prefix each part with its length. Hash a part first if it may contain
the separator.

### time-equality

**Ledger time compared for equality.** It reports `==` or `/=` where one operand is the
ledger time read with `getTime` (or a `let` alias of it).

**Impact:** ledger time has microsecond resolution and the submitting participant picks it
within the allowed skew, so it practically never equals a given instant. `now == t` is
always False, so a choice that requires it can never run; `now /= t` is always True, so a
guard built on it never stops anything.

**Example** (`examples/vulnerable/time-equality/daml/Main.daml`):

```haskell
    choice Close : ()
      controller seller
      do
        now <- getTime
        assertMsg "not closed yet" (now == closesAt)

    choice Bid : ContractId Auction
      with
        amount : Decimal
      controller bidder
      do
        now <- getTime
        if now /= closesAt
          then create this with price = amount
          else abort "closed"
```

```
$ damlisk scan examples/vulnerable/time-equality/time-equality.dar --detect time-equality
[Medium] time-equality Main.daml:19
    Main:Auction.Bid.update: ledger time compared with `/=`
[Medium] time-equality Main.daml:13
    Main:Auction.Close.update: ledger time compared with `==`
2 finding(s).
```

`SafeClose` (`now >= closesAt`) and `Extend` (`newClose /= closesAt`, two stored times, no
ledger time) are not reported.

**How it works:** variables bound to `getTime` (the `get_time` update, `getTime` /
`$cgetTime`, or a compiler helper wrapping them) and their `let` aliases are collected per
body; any equality test (`EQUAL`, `==` / `/=` methods, partially applied helpers) taking one
of them as an argument is reported.

**Results on real code:** Splice is clean: 17 bodies in `splice-amulet` and
`splice-wallet-payments` read the ledger time, and all of them use ordering comparisons or
`isLedgerTime*` helpers.

**Recommendation:** use an ordering (`now >= closesAt`), or `assertDeadlineExceeded` /
`assertWithinDeadline` / `isLedgerTimeGE`, which also work when the ledger time is only
known within bounds.

### tautological-compare

**Value compared with itself.** It reports `==`, `/=`, `<`, `<=`, `>`, `>=` whose two
operands are the same variable or the same field of the same record.

**Impact:** the result is fixed (`==`, `<=`, `>=` always True; `/=`, `<`, `>` always False).
This is almost always a typo for another field, so the check the author meant is missing: a
guard that always passes lets anyone through, one that always fails blocks the choice.

**Example** (`examples/vulnerable/tautological-compare/daml/Main.daml`):

```haskell
    ensure amount > 0.0 && price >= price

    choice Settle : ()
      with
        payer : Party
      controller taker
      do
        assertMsg "payer is taker" (payer == payer)
        pure ()

    choice Reprice : ContractId Swap
      with
        newPrice : Decimal
      controller maker
      do
        assertMsg "price changed" (newPrice /= newPrice)
        create this with price = newPrice
```

```
$ damlisk scan examples/vulnerable/tautological-compare/tautological-compare.dar --detect tautological-compare
[Medium] tautological-compare Main.daml:22
    Main:Swap.Reprice.update: value compared with itself by `/=`, always False
[Medium] tautological-compare Main.daml:14
    Main:Swap.Settle.update: value compared with itself by `==`, always True
[Medium] tautological-compare Main.daml:12
    Main:Swap.precond: value compared with itself by `>=`, always True
3 finding(s).
```

`SafeSettle` (`payer == taker`) and `SafeReprice` (`newPrice /= price`) are not reported.

**How it works:** damlc binds each field read once (`let ds4 = arg.newPrice`), so a field
compared with itself becomes the same variable on both sides. Operators are found through
builtins, `Eq`/`Ord` methods and alias helpers. The derived `Eq` instances compare `a1` with
`b1` and are not reported.

**Results on real code:** Splice is clean.

**Recommendation:** compare with the intended value, or remove the check.

### unprotected-archive

**Archive by a non-signatory.** It reports a consuming choice whose controllers are contract
parties none of which is a signatory (Slither `suicidal`).

**Impact:** exercising a consuming choice archives the contract. When only an observer
controls it, a party that never signed the contract can destroy it, and the signatories lose
it without consent.

**Example** (`examples/vulnerable/unprotected-archive/daml/Main.daml`):

```haskell
template Asset
  with
    issuer : Party
    owner : Party
    auditor : Party
  where
    signatory issuer
    observer owner, auditor

    choice Cancel : ()
      controller auditor
      do pure ()

    choice Burn : ()
      controller owner
      do pure ()
```

```
$ damlisk scan examples/vulnerable/unprotected-archive/unprotected-archive.dar --detect unprotected-archive
[High] unprotected-archive Main.daml:16
    Main:Asset.Burn: archived by non-signatory controller `owner`
[High] unprotected-archive Main.daml:12
    Main:Asset.Cancel: archived by non-signatory controller `auditor`
2 finding(s).
```

`Revoke` (`controller issuer`), `Redeem` (`controller owner, issuer`) and the nonconsuming
`Inspect` are not reported.

**How it works:** the template fields read by `signatory` and by the choice's `controller`
are traced with field flow. A consuming template choice is reported when its controller
fields are not empty and share no field with the signatory fields. Controllers taken from the
choice argument are left to [`controller-from-argument`](#controller-from-argument).

**Results on real code:** `splice-amulet` 0.1.24 has 12 findings (0.1.14 has 10). They are
proposal and delegation choices where an observer ends the contract by design, e.g.
`ExternalPartySetupProposal_Accept` / `_Reject` (`user`), `DevelopmentFundCoupon_Withdraw`
(`fundManager`), `FeaturedAppRight_Cancel` (`provider`), `TransferCommand_Send` (`delegate`)
and five `ValidatorLicense_*` choices (`validator`). Review that ending the contract is the
intent of each.

**Recommendation:** make the choice `nonconsuming`, add a signatory as co-controller, or make
the controller a signatory. Keep consuming observer choices only where ending the contract
is their purpose (rejecting a proposal) and document it.

### missing-ensure

**Missing template invariant.** It reports a template that has `Numeric`, `Int` or `Time`
fields but no `ensure` clause, or only `ensure True`.

**Impact:** without an invariant the ledger accepts contracts with any value in those fields:
negative amounts, zero or negative counters, inverted time windows. Every choice that adds,
compares or schedules with them inherits the bad value.

**Example** (`examples/vulnerable/missing-ensure/daml/Main.daml`):

```haskell
template Holding
  with
    owner : Party
    amount : Decimal
  where
    signatory owner

template Lock
  with
    owner : Party
    unlockAt : Time
  where
    signatory owner
    ensure True
```

```
$ damlisk scan examples/vulnerable/missing-ensure/missing-ensure.dar --detect missing-ensure
[Medium] missing-ensure Main.daml:18
    Main:Counter: no ensure constrains `count`
[Medium] missing-ensure Main.daml:3
    Main:Holding: no ensure constrains `amount`
[Medium] missing-ensure Main.daml:10
    Main:Lock: no ensure constrains `unlockAt`
3 finding(s).
```

`SafeHolding` (`ensure amount > 0.0`) and `Note` (only `Party` and `Text` fields) are not
reported.

**How it works:** damlc compiles both a missing `ensure` and `ensure True` to
`$censure = \this -> True`; the detector follows the `ensure` helper and checks for that
constant. Only direct template fields of type `Numeric`, `Int` or `Time` count. Unlike
[`missing-amount-check`](#missing-amount-check), which reports each `Numeric` field the
`ensure` never mentions, this reports templates that have no invariant at all.

**Results on real code:** `splice-amulet` 0.1.24 has 6 findings, the same 6 templates a source
scan finds without `ensure`: `CalculateRewardsV2`, `ProcessRewardsV2`,
`ExternalPartySetupProposal`, `TransferCommand` (`amount`, `expiresAt`, `nonce`),
`TransferCommandCounter` (`nextNonce`) and `ExternalPartyConfigState`. 0.1.14 has 3.

**Recommendation:** add an `ensure` that states the invariants, e.g. `ensure amount > 0.0`,
`ensure nonce >= 0`, `ensure createdAt <= expiresAt`.

### over-disclosure

**Choice observers taken from the choice argument.** It reports a choice whose `observer`
clause uses fields of the choice argument.

**Impact:** choice observers see the exercise and everything it creates, fetches or
exercises. When the controller picks them, the controller can divulge the contract and its
consequences to any party.

**Example** (`examples/vulnerable/over-disclosure/daml/Main.daml`):

```haskell
    choice Settle : ()
      with
        watchers : [Party]
      observer watchers
      controller owner
      do pure ()

    choice Report : ()
      with
        reader : Party
        note : Text
      observer [reader, auditor]
      controller owner
      do pure ()
```

```
$ damlisk scan examples/vulnerable/over-disclosure/over-disclosure.dar --detect over-disclosure
[Medium] over-disclosure Main.daml:19
    Main:Trade.Report: choice observers taken from argument `reader`
[Medium] over-disclosure Main.daml:12
    Main:Trade.Settle: choice observers taken from argument `watchers`
2 finding(s).
```

`Audit` (`observer auditor`, a contract field) and `Peek` (no choice observers) are not
reported.

**How it works:** the detector traces the choice argument through the `observers` expression
of each choice, following package helpers. Only named argument fields count: an observer
computed by an interface method from the whole argument (`observer
allocation_settleExtraObservers this arg`) is chosen by the implementation and is not
reported. Template observers set when a choice creates a contract need data flow across
`create` (T2) and are not covered.

**Results on real code:** `splice-amulet` 0.1.24 has 7 findings, all DSO-controlled choices
that take observers from the argument (`expiryObservers`, `providers`, `observers`,
`batch`); 0.1.14 has none. `splice-api-featured-app-v2` (`beneficiaries`) and
`splice-api-reward-assignment-v1` (`newBeneficiaries`) have 1 each.

**Recommendation:** take choice observers from contract fields that the signatories agreed
to, or check the argument parties against an allowed list before they are used as observers.

### unsafe-primitive

**Unchecked cast.** It reports `coerceContractId` (`COERCE_CONTRACT_ID`),
`unsafeFromInterface` (`unsafe_from_interface`) and `from_any` in code the package author
wrote.

**Impact:** these change the static type of a contract id or value without a check. The
code then trusts a template type that the ledger never confirmed, e.g. it exercises a choice
of one template on a contract id the caller supplied for another.

**Example** (`examples/vulnerable/unsafe-primitive/daml/Main.daml`):

```haskell
    nonconsuming choice Peek : Decimal
      with
        cid : ContractId Vault
      controller keeper
      do
        holding <- fetch (coerceContractId cid : ContractId Holding)
        pure holding.amount

    nonconsuming choice Unwrap : Decimal
      with
        cid : ContractId Asset
      controller keeper
      do
        asset <- fetch cid
        let holding = unsafeFromInterface cid asset : Holding
        pure holding.amount
```

```
$ damlisk scan examples/vulnerable/unsafe-primitive/unsafe-primitive.dar --detect unsafe-primitive
[High] unsafe-primitive Main.daml:23
    Main:Vault.Peek.update: unsafe primitive `coerceContractId`
[High] unsafe-primitive Main.daml:31
    Main:Vault.Unwrap.update: unsafe primitive `unsafeFromInterface`
2 finding(s).
```

`Check` (`fromInterface` with an `Optional` result), `Upcast` (`toInterfaceContractId`) and
`Downcast` (`fetch (fromInterfaceContractId @Holding cid)`) are not reported.

**How it works:** the detector looks at every expression for the `COERCE_CONTRACT_ID`
builtin, the stdlib values `coerceContractId` and `unsafeFromInterface`, the instance method
`$cunsafeFromInterfaceN` that damlc calls for `unsafeFromInterface` on a template, and the
`unsafe_from_interface` and `from_any` nodes. It does not follow stdlib wrappers, because
the safe upcast `toInterfaceContractId` is itself built on `coerceContractId`. The
`HasFromAny*` and `HasFromInterface*` instances that damlc generates for every template are
skipped, and so are instance dictionaries: a `fetch` after `fromInterfaceContractId` pulls in
the `HasFromInterface` dictionary, which only lists `$cunsafeFromInterfaceN` as a method.

**Results on real code:** `splice-amulet` 0.1.24 has 3 findings, the 3 `coerceContractId`
calls in the source (`TokenApiUtils.daml:283`, `:327`, `TwoStepTransfer.daml:61`); 0.1.14
has the same 3. `splice-token-standard-utils` has 8, one per `coerceContractId` call in
`Allocations.daml` and `Conversions.daml`.

**Recommendation:** use the checked forms: `fromInterface` with a `case` on the result,
`fetchFromInterface` or `fromAnyTemplate`, and fetch the contract to confirm its template
before using it.

### debug-trace

**Debug trace left in production code.** It reports each `trace`, `traceRaw`, `traceId`,
`debug` and `debugRaw` call, and the `TRACE` builtin they compile to.

**Impact:** the message is written to the log of every participant that runs the code.
Operators and log pipelines then read amounts, parties and other data the ledger keeps
private.

**Example** (`examples/vulnerable/debug-trace/daml/Main.daml`):

```haskell
    choice Withdraw : ContractId Account
      with
        amount : Decimal
      controller owner
      do
        debug ("withdraw " <> show amount)
        create this with balance = balance - amount

fee : Decimal -> Decimal
fee amount = traceRaw "fee" (amount * 0.01)
```

```
$ damlisk scan examples/vulnerable/debug-trace/debug-trace.dar --detect debug-trace
[Informational] debug-trace Main.daml:26
    Main:Account.Close.update: debug output `debugRaw`
[Informational] debug-trace Main.daml:18
    Main:Account.Deposit.update: debug output `trace`
[Informational] debug-trace Main.daml:32
    Main:Account.Report.update: debug output `traceId`
[Informational] debug-trace Main.daml:10
    Main:Account.Withdraw.update: debug output `debug`
[Informational] debug-trace Main.daml:41
    Main:fee: debug output `traceRaw`
5 finding(s).
```

`Peek` (no trace) is not reported.

**How it works:** the detector looks at every expression for the `TRACE` builtin and the five
`DA.Internal.Prelude` functions built on it. damlc moves code of a top-level function into
`$$sc_...` helpers; these are reported under the function that calls them (`Main:fee`), the
same way helpers of a choice are reported under the choice.

**Results on real code:** `splice-amulet` 0.1.14 and 0.1.19 have 3 findings each, the three
`trace` calls in `summarizeTransfer` (`AmuletRules.daml:1014`,
`trace summary $ trace preprocessedOutputs $ trace inp $ pure summary`). They are gone in
0.1.24, which has none.

**Recommendation:** remove debug output before release, or keep it in Daml Script tests.

### stuck-asset

**Asset its owner cannot move.** It reports a template with an `owner` or `holder` field when
no consuming choice other than `Archive` is controlled by that field.

**Impact:** the holder cannot transfer, split or redeem the asset alone. Other parties decide
when, or whether, it moves.

**Example** (`examples/vulnerable/stuck-asset/daml/Main.daml`):

```haskell
template Holding
  with
    issuer : Party
    owner : Party
    amount : Decimal
  where
    signatory issuer, owner

    choice Freeze : ContractId Holding
      controller issuer
      do create this

template Badge
  with
    issuer : Party
    holder : Party
  where
    signatory issuer
    observer holder

    nonconsuming choice Present : Party
      controller holder
      do pure issuer
```

```
$ damlisk scan examples/vulnerable/stuck-asset/stuck-asset.dar --detect stuck-asset
[Medium] stuck-asset Main.daml:15
    Main:Badge: `holder` controls no consuming choice except Archive
[Medium] stuck-asset Main.daml:3
    Main:Holding: `owner` controls no consuming choice except Archive
2 finding(s).
```

`Token` (`Transfer` controlled by `owner`), `Voucher` (`Redeem` controlled by `holder, issuer`)
and `Note` (no `owner` or `holder` field) are not reported.

**How it works:** for each template with a field named `owner` or `holder`, the detector
traces the controllers of every consuming template choice except `Archive` and checks whether
one of them is that field. Nonconsuming choices do not count, since they leave the asset where
it is. Choices of implemented interfaces are not decoded and are not considered.

**Results on real code:** `splice-amulet` (0.1.14 to 0.1.24) has 1 finding, `Amulet`. Its
only consuming choices (`Amulet_Expire`, `Amulet_ExpireV2`) are controlled by `dso`; the owner
moves amulets through `AmuletRules_Transfer` on the `AmuletRules` contract, which archives them.
This is the rules-contract design the recommendation mentions, so review rather than fix.

**Recommendation:** give the holder a consuming choice (`Transfer`, `Redeem`, `Split`) or
document the contract, often a rules contract, through which the holder moves the asset.

### sdk-version

**Daml-LF 1.x target.** It reports a DAR whose main package was compiled for Daml-LF 1.x, i.e.
with a Daml 2.x SDK.

**Impact:** Canton 3 and Splice run Daml-LF 2.x packages only, and LF 1.x packages lack smart
contract upgrades, so a fix cannot be rolled out as an upgrade of the deployed package.

**Example:** a DAR built with SDK 2.9 and `--target=1.15`:

```
$ damlisk scan old-token.dar --detect sdk-version
[Informational] sdk-version old-token
    old-token: built for Daml-LF 1.15 (SDK 2.9.4)
1 finding(s).
```

**How it works:** the detector reads the LF version of the main package from its archive
payload and the SDK from the manifest `Sdk-Version`. There is no example project: the SDKs
installed for this repository are 3.x and only build LF 2.x; the tests give a Splice DAR an
LF 1.x main package instead.

**Results on real code:** all Splice DARs target Daml-LF 2.1 (SDK 3.3 to 3.5) and have no
findings.

**Recommendation:** rebuild the package with a Daml 3.x SDK for a Daml-LF 2.x target.

### rtlo

**Right-to-left override.** It reports U+202E and the other Unicode bidirectional control
characters (U+202A–U+202E, U+2066–U+2069) in the embedded `.daml` sources and in `Text`
literals.

**Impact:** these characters reorder the text around them when it is displayed. In a comment
the source a reviewer reads differs from the code that runs; in a `Text` value a name or label
shown to users differs from its content.

**Example** (`examples/vulnerable/rtlo/daml/Main.daml`):

```haskell
    choice Transfer : ContractId Asset
      with
        to : Party
      controller owner
      do
        -- only the owner may transfer <U+202E> } ;owner =/= ot ecnetsixe {
        create this with owner = to

    choice Rename : ContractId Asset
      controller owner
      do create this with label = "invoice\x202Etxt.exe"
```

The comment renders as `-- only the owner may transfer { existence to /= owner; }`, and the
label renders as `invoiceexe.txt`.

```
$ damlisk scan examples/vulnerable/rtlo/rtlo.dar --detect rtlo
[High] rtlo Main.daml:15
    Main: bidirectional control character U+202E in source
[High] rtlo Main.daml:18
    Main:Asset.Rename.update: Text literal contains U+202E
2 finding(s).
```

`Relabel` (`label = "invoice.pdf"`) is not reported.

**How it works:** damlc rejects a raw bidirectional character inside a string literal
(`lexical error in string/character literal`), but accepts it in comments, and accepts escapes
such as `\x202E` in literals, which compile to the real character in the Daml-LF literal. The
detector therefore scans every line of the sources embedded in the DAR, and every `Text`
literal in the package. Right-to-left letters (Hebrew, Arabic) are not control characters and
are not reported.

**Results on real code:** no Splice source or literal contains a bidirectional control
character.

**Recommendation:** remove bidirectional control characters from sources and literals, and
reject them in `Text` fields that are shown to users.
