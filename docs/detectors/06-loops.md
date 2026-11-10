# Loops detectors

Ledger work inside loops and loops over caller-sized lists.

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`ledger-op-in-loop`](#ledger-op-in-loop) | Low | Medium | Create, exercise or fetch inside a loop |
| [`unbounded-input-loop`](#unbounded-input-loop) | Medium | Medium | Loop over a list from the choice argument with no length check |

## ledger-op-in-loop

**Create, exercise or fetch inside a loop.** It reports a choice that runs `create`,
`exercise` (including `archive`) or `fetch` inside the closure of `forA`, `forA_`, `mapA`,
`mapA_`, `forM`, `mapM`, `foldl`, `foldr`, `foldlA` or `foldrA`.

**Impact:** every iteration adds nodes to the transaction, so a long list can exceed
transaction limits. All iterations commit or abort together: one failing iteration, such as
an archived contract or a failed check, blocks the rest.

**Example** (`examples/vulnerable/ledger-op-in-loop/daml/Main.daml`):

```haskell
    nonconsuming choice PayAll : ()
      with
        payees : [(Party, Decimal)]
      controller owner
      do forA_ payees \(p, a) -> exercise cashCid Pay with to = p; amt = a

    nonconsuming choice Total : Decimal
      with
        amounts : [Decimal]
      controller owner
      do pure (foldl (+) 0.0 amounts)
```

```text
$ damlisk scan examples/vulnerable/ledger-op-in-loop/ledger-op-in-loop.dar --detect ledger-op-in-loop
[Low] ledger-op-in-loop Main.daml:47
    Main:Treasury.ArchiveAll: exercise inside a loop
[Low] ledger-op-in-loop Main.daml:35
    Main:Treasury.MintAll: create inside a loop
[Low] ledger-op-in-loop Main.daml:41
    Main:Treasury.MintByHelper: create inside a loop
[Low] ledger-op-in-loop Main.daml:29
    Main:Treasury.PayAll: exercise inside a loop
[Low] ledger-op-in-loop Main.daml:53
    Main:Treasury.ReadAll: fetch inside a loop
5 finding(s).
```

`Total` (a pure fold), `MintOne` (no loop) and `Label` (a pure `map`) are not reported.

**How it works:** the detector looks for calls of the loops above, in the choice body and in
the package helpers it calls, and searches every argument of the loop for ledger operations.
It follows lambdas and package helpers, so `forA_ cids archive` and `mapA (mint owner) names`
count. The size of the list is not considered; a loop over a fixed template field is
reported the same as one over a choice argument (that case is
`unbounded-input-loop`).

**Results on real code:** `splice-amulet` 0.1.24 has 20 findings, 0.1.19 has 19 and 0.1.14
has 9. They are intended batches, for example `AmuletRules_ClaimExpiredRewards` expiring a
list of reward coupons and `AmuletRules_Transfer` consuming the transfer inputs.

**Recommendation:** bound the number of iterations, or split the work into one choice per
item so a single failure only affects that item.

## unbounded-input-loop

**Loop over a list from the choice argument with no length check.** It reports a choice that
runs `create`, `exercise` or `fetch` inside `forA`, `mapA`, `foldl` or another loop from
[`ledger-op-in-loop`](#ledger-op-in-loop) over a list field of its argument, when nothing
compares `length` of that list with `<`, `<=`, `>` or `>=`.

**Impact:** the submitter decides how many iterations run. A long list makes the transaction
too large to commit, or creates that many contracts under the signatories' authority.

**Example** (`examples/vulnerable/unbounded-input-loop/daml/Main.daml`):

```haskell
    nonconsuming choice PayAll : ()
      with
        payees : [(Party, Decimal)]
      controller owner
      do forA_ payees \(p, a) -> exercise cashCid Pay with to = p; amt = a

    nonconsuming choice PayCapped : ()
      with
        payees : [(Party, Decimal)]
      controller owner
      do
        assertMsg "too many payees" (length payees <= 50)
        forA_ payees \(p, a) -> exercise cashCid Pay with to = p; amt = a
```

```text
$ damlisk scan examples/vulnerable/unbounded-input-loop/unbounded-input-loop.dar --detect unbounded-input-loop
[Medium] unbounded-input-loop Main.daml:42
    Main:Treasury.MintAll: loop over argument `names` with no length check
[Medium] unbounded-input-loop Main.daml:30
    Main:Treasury.PayAll: loop over argument `payees` with no length check
[Medium] unbounded-input-loop Main.daml:36
    Main:Treasury.PayByHelper: loop over argument `payees` with no length check
[Medium] unbounded-input-loop Main.daml:68
    Main:Treasury.PayNonEmpty: loop over argument `payees` with no length check
4 finding(s).
```

`PayNonEmpty` is reported because `not (null payees)` only rules out an empty list. `PayCapped`
(the length is checked), `PayMembers` (the list is a template field) and `Total` (a pure
`foldl` with no ledger operation) are not reported.

**How it works:** the detector follows the argument fields through `let`, package helpers and
library calls to the list a loop runs over: the list before the callback for `forA` and
`forM`, the last argument for `mapA` and the folds. Only fields of type `[a]` or
`Optional [a]` count, and only loops whose callback runs a ledger operation. A length check
is an ordering comparison on `length xs`, also after arithmetic such as
`length xs * fee < cap`; a comparison on the elements or on `sum xs` does not count. Lists
nested inside a record of the argument, such as `transfer.inputs`, are not followed.

**Results on real code:** `splice-amulet` 0.1.24 has 10 findings, 0.1.19 has 9 and 0.1.14 has
3; all are DSO choices that process a list of coupons or contracts passed by the DSO
automation, for example `AmuletRules_ClaimExpiredRewards` and
`AmuletRules_MergeMemberTrafficContracts`.

**Recommendation:** check the length first, for example
`assertMsg "too many" (length payees <= 50)`, or split the work into several transactions.
