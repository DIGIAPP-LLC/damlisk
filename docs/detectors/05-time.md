# Time detectors

Ledger time used for decisions or randomness.

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`time-dependence`](#time-dependence) | Low | Medium | Ledger time decides a branch |
| [`weak-randomness`](#weak-randomness) | High | Medium | Ledger time or a hash picks a list element or map entry |

## time-dependence

**Ledger time decides a branch.** It reports a choice that reads the ledger time (`getTime`,
`isLedgerTimeLT`, `assertWithinDeadline`, `assertDeadlineExceeded`, ...) and lets it decide an
`if`, a `case` or an assertion.

**Impact:** the submitting participant picks the ledger time within the allowed skew. For a
transaction close to a deadline, the submitter decides which side of the deadline it lands on.
The check marks where that matters; most such branches are intended, which is why it is rated
Low.

**Example** (`examples/vulnerable/time-dependence/daml/Main.daml`):

```haskell
    choice Bid : ContractId Auction
      with
        price : Decimal
      controller bidder
      do
        now <- getTime
        assertMsg "closed" (now < closesAt)
        create this with best = price

    nonconsuming choice Stamp : ContractId Log
      controller seller
      do
        now <- getTime
        create Log with seller; at = now
```

```text
$ damlisk scan examples/vulnerable/time-dependence/time-dependence.dar --detect time-dependence
[Low] time-dependence Main.daml:25
    Main:Auction.Bid: ledger time decides a branch
[Low] time-dependence Main.daml:19
    Main:Auction.Close: ledger time decides a branch
[Low] time-dependence Main.daml:40
    Main:Auction.Expire: ledger time decides a branch
[Low] time-dependence Main.daml:34
    Main:Auction.Settle: ledger time decides a branch
[Low] time-dependence Main.daml:44
    Main:Auction.Withdraw: ledger time decides a branch
5 finding(s).
```

`Stamp` (the time is only stored), `Reprice` (no time) and `Reschedule` (a `Time` from the
argument, which [`time-from-argument`](04-validation.md#time-from-argument) covers) are not reported.

**How it works:** a variable bound to `getTime` or to a ledger-time test such as
`isLedgerTimeLT` carries the ledger time. The detector follows it through `let`, package
helpers and library functions such as `assertMsg` and `assertDeadlineExceeded`, and reports
the choice when it reaches the condition of a `case`. Time that flows into an amount, and the
size of the skew window, are not checked. A helper that reads the time but receives no
argument from the choice is not followed.

**Results on real code:** `splice-amulet` 0.1.24 has 29 findings and `splice-wallet-payments`
0.1.24 has 5. Each is an expiry or deadline check, for example `TransferPreapproval_Send` and
`ValidatorLicense_UpdateMetadata`, which allows a metadata update only after a minimum
interval.

**Recommendation:** keep time windows much longer than the skew, accept that a deadline is
fuzzy by the skew, and never rely on ledger time for ordering or exact instants.

## weak-randomness

**Ledger time or a hash picks a list element or map entry.** It reports a choice that uses
the ledger time (`getTime`) or a `sha256`/`keccak256` hash as randomness and lets it reach the
index of `!!`, or that uses the ledger time as the key of a map lookup.

**Impact:** the submitter chooses the ledger time within the skew window and can compute any
hash of ledger data in advance, so the pick is predictable and can be steered, for example
the winner of a draw.

**Example** (`examples/vulnerable/weak-randomness/daml/Main.daml`):

```haskell
    choice DrawByTime : ContractId Prize
      controller host
      do
        now <- getTime
        let us = micros now started
        let winner = players !! (us % length players)
        create Prize with host; winner

    choice DrawByArg : ContractId Prize
      with
        pick : Int
      controller host
      do
        let winner = players !! (pick % length players)
        create Prize with host; winner
```

```text
$ damlisk scan examples/vulnerable/weak-randomness/weak-randomness.dar --detect weak-randomness
[High] weak-randomness Main.daml:33
    Main:Lottery.DrawByHash: a hash picks a list element
[High] weak-randomness Main.daml:41
    Main:Lottery.DrawByHelper: ledger time picks a list element
[High] weak-randomness Main.daml:55
    Main:Lottery.DrawByMap: ledger time picks a map entry
[High] weak-randomness Main.daml:25
    Main:Lottery.DrawByTime: ledger time picks a list element
4 finding(s).
```

`DrawByArg` (the index comes from the argument), `FindByHash` (a map lookup keyed by a
hash), `Seal` (the hash is only stored) and
`Close` (the time only decides a branch, which [`time-dependence`](#time-dependence) covers)
are not reported.

**How it works:** a variable bound to `getTime` carries the ledger time and the result of
`sha256` or `keccak256` carries a hash, whatever it was computed from. The detector follows
both through `let`, arithmetic, package helpers and library functions, and reports the choice
when either reaches an argument of `DA.List.!!`, or when the ledger time reaches an argument
of a map lookup (`lookup`, `member` and `findWithDefault` of `DA.Map` and `DA.TextMap`, and
the `GenMap` builtin). A map lookup keyed by a hash is not reported, because a hash is a
common key that identifies an entry rather than selects one at random. Other ways of
selecting, such as a `case` on `seed % n` or sorting by a hash, are not checked.

**Results on real code:** no findings on `splice-amulet`, `splice-wallet-payments` or
`splice-util`; none of them indexes a list with time or a hash, or looks up a map by time.

**Recommendation:** do not derive randomness on the ledger. Use a commit-reveal scheme
between the parties or an external randomness source whose result is signed and verified.
