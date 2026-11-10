# Validation detectors

Inputs, amounts and results that are not checked.

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`missing-amount-check`](#missing-amount-check) | Low | Medium | `Decimal` template field not constrained by `ensure` |
| [`partial-function`](#partial-function) | Low | Medium | Choice argument passed to `head`, `fromSome`, `!!`, ... |
| [`nonconsuming-create`](#nonconsuming-create) | High | Medium | Nonconsuming choice creates its own template without archiving `self` |
| [`unchecked-fetch`](#unchecked-fetch) | High | Medium | Contract fetched from a choice argument and used without validation |
| [`time-from-argument`](#time-from-argument) | Medium | Medium | Deadline logic on a caller-supplied `Time` instead of ledger time |
| [`amount-tolerance`](#amount-tolerance) | Medium | High | `Decimal` amounts compared with `abs (a - b) < eps` instead of exactly |
| [`divide-before-multiply`](#divide-before-multiply) | Medium | Medium | Result of a division multiplied, compounding its rounding error |
| [`unconsumed-input`](#unconsumed-input) | High | Medium | Input contract of the same template read but not archived |
| [`hash-concat-collision`](#hash-concat-collision) | Medium | Medium | `sha256` of texts joined without a separator |
| [`time-equality`](#time-equality) | Medium | High | Ledger time compared with `==` or `/=` |
| [`missing-ensure`](#missing-ensure) | Medium | High | Template with amount or time fields and no or trivial `ensure` |
| [`ignored-optional`](#ignored-optional) | Medium | Medium | `Optional` result discarded or forced with `fromSome` |

## missing-amount-check

**Amount not checked by ensure.** It reports `Decimal` /
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

## partial-function

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

## nonconsuming-create

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

## unchecked-fetch

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

## time-from-argument

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

## amount-tolerance

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

## divide-before-multiply

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

## unconsumed-input

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

## hash-concat-collision

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

## time-equality

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

## missing-ensure

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

## ignored-optional

**`Optional` result discarded or forced with `fromSome`.** It reports a `do` block that binds
an `Optional` result, for example `r <- lookupByKey @T k` or an exercise of a choice that
returns `Optional`, and then never uses it or passes it straight to `fromSome`.

**Impact:** an unused result usually means a lookup that was meant as a check is never
checked. `fromSome` turns the `None` case into an abort with a generic error instead of a
handled failure.

**Example** (`examples/vulnerable/ignored-optional/daml/Main.daml`):

```haskell
    nonconsuming choice CheckOnly : ()
      with
        name : Party
      controller admin
      do
        found <- exercise self Find with name
        pure ()

    nonconsuming choice ForceFind : Party
      with
        name : Party
      controller admin
      do
        found <- exercise self Find with name
        pure (fromSome found)
```

```text
$ damlisk scan examples/vulnerable/ignored-optional/ignored-optional.dar --detect ignored-optional
[Medium] ignored-optional Main.daml:18
    Main:Registry.CheckOnly.update: `found` is never used
[Medium] ignored-optional Main.daml:26
    Main:Registry.ForceFind.update: `found` is forced with fromSome
[Medium] ignored-optional Main.daml:34
    Main:Registry.ForceHelper.update: `found` is forced with fromSome
3 finding(s).
```

`Matched` (`case found of None -> abort ...`), `Noted` (`fromSomeNote`) and `Defaulted`
(`fromOptional`) are not reported.

**How it works:** for each binding of an update `do` block whose type is `Optional`, it
reports the binding when the variable is not mentioned by a later binding or the body, or
when it is passed directly to `DA.Optional.fromSome`. Pure `let` bindings are skipped, so
`fromSome` on a choice argument is left to `partial-function`. A value forced inside a
helper after being passed on, or via `fromJust`, is not followed.
