# Contracts detectors

Contract ids and contract state taken from untrusted places or used after they change.

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`unsafe-primitive`](#unsafe-primitive) | High | High | Unchecked cast of a contract id, interface or `Any` value |
| [`untrusted-interface-exercise`](#untrusted-interface-exercise) | High | Medium | Interface contract id from the choice argument is exercised or fetched |
| [`stale-fetch`](#stale-fetch) | Medium | Medium | Fetched value used after the contract was replaced by a successor |

## unsafe-primitive

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

## untrusted-interface-exercise

**Interface contract id from the choice argument is exercised or fetched.** It reports a
choice that exercises or fetches an interface contract whose id comes from the choice
argument, when the contract has a signatory other than the controller.

**Impact:** the controller picks the contract, so the implementation behind the interface can
come from any vetted package. When the exercised interface choice is controlled by a party
whose authority the current choice holds, the implementation runs with that party's authority
and can create or exercise anything in that party's name. A fetch runs no ledger action, but
its view is whatever the implementation returns.

**Example** (`examples/vulnerable/untrusted-interface-exercise/daml/Main.daml`):

```haskell
template Desk
  with
    bank : Party
    trader : Party
    stored : ContractId Holding
  where
    signatory bank
    observer trader

    nonconsuming choice Settle : ()
      with
        holdingCid : ContractId Holding
        receiver : Party
      controller trader
      do exercise holdingCid Send with receiver

    nonconsuming choice SettleAll : ()
      with
        cids : [ContractId Holding]
        receiver : Party
      controller trader
      do forA_ cids (\cid -> exercise cid Send with receiver)

    nonconsuming choice Inspect : Decimal
      with
        holdingCid : ContractId Holding
      controller trader
      do
        holding <- fetch holdingCid
        pure (view holding).amount
```

```
$ damlisk scan examples/vulnerable/untrusted-interface-exercise/untrusted-interface-exercise.dar --detect untrusted-interface-exercise
[High] untrusted-interface-exercise Main.daml:62
    Main:Desk.Inspect: interface contract id from argument `holdingCid`
[High] untrusted-interface-exercise Main.daml:48
    Main:Desk.Settle: interface contract id from argument `holdingCid`
[High] untrusted-interface-exercise Main.daml:55
    Main:Desk.SettleAll: interface contract id from argument `cids`
[High] untrusted-interface-exercise Main.daml:106
    Main:Pool.Drain: interface contract id from argument `holdingCid`
4 finding(s).
```

`SettleStored` (the id is a contract field), `PayCash` (a concrete template), `SendCash` (an
argument declared `ContractId Cash` and cast for the exercise), `BankSettle` and `Vault.Sweep`
(the controller is the only signatory, so only their own authority is at risk) are not
reported. `Pool.Drain` is reported because `bank` also signs the pool.

**How it works:** the detector traces the choice argument through the choice body, following
package helpers and callbacks such as `forA_`, and collects the fields that reach an interface
exercise or an interface fetch. Fields whose contract ids all name templates, such as
`ContractId T`, `[ContractId T]` or a record of such ids, are dropped. Variants are not
searched, so an interface id inside a variant field is dropped too. The declared type is not enforced on a contract id, so a choice that
casts such a field to an interface without fetching it first is not reported. Interface
choices and interface method implementations are not checked. Checks on the view are not
counted, because the implementation controls the view.

**Results on real code:** the Splice packages have no finding. `splice-amulet` 0.1.24 casts
`externalPartyConfigState0Cid` to an interface in `Amulet_ExpireV2`, but declares it as a
template id and fetches it first. `AmuletRules_CreateTransferPreapproval` and two other
choices cast `context.amuletRules` to an interface the same way; `context` is a record that
holds only template ids. The token-standard API packages exercise interfaces from
their own choices, which the check skips. Splice documents the same risk on `expectedAdmin` in
`TransferFactory_Transfer`: exercising a factory from an untrusted source is safe only
"provided all vetted Daml packages only contain interface implementations that check the
expected admin party".

**Recommendation:** store the contract id on the contract, check the implementation's admin
against a trusted party inside a vetted implementation, or exercise a concrete template.

## stale-fetch

**Fetched value used after the contract was replaced by a successor.** It reports a choice
that fetches a contract, then exercises a consuming choice on the same contract id that
returns a new `ContractId` of the same template, and uses the fetched value after that.

**Impact:** the fetched value describes the version that was just archived. After a choice
such as `Withdraw` the real state lives in the successor, so amounts or parties taken from
the fetched value are out of date.

**Example** (`examples/vulnerable/stale-fetch/daml/Main.daml`):

```haskell
    nonconsuming choice PayOut : ContractId Receipt
      with
        cid : ContractId Account
      controller owner
      do
        acc <- fetch cid
        _ <- exercise cid Withdraw with amt = 10.0
        create Receipt with bank; owner; remaining = acc.amount

    nonconsuming choice Merge : ContractId Account
      with
        cid : ContractId Account
        other : ContractId Account
      controller owner
      do
        acc <- fetch other
        archive other
        exercise cid Withdraw with amt = negate acc.amount
```

```text
$ damlisk scan examples/vulnerable/stale-fetch/stale-fetch.dar --detect stale-fetch
[Medium] stale-fetch Main.daml:29
    Main:Desk.PayOut: `acc` is used after `Withdraw`
[Medium] stale-fetch Main.daml:38
    Main:Desk.PayTwice: `acc` is used after `Withdraw`
2 finding(s).
```

`Merge` (fetch, `Archive`, then use of the fetched value, the usual merge pattern),
`Refresh` (fetches the successor), `ReadFirst` (computes the new value before the exercise)
and `Look` (a nonconsuming choice) are not reported.

**How it works:** in each `do` block of the choice and of the package helpers it calls, the
detector pairs `x <- fetch cid` with a later `exercise cid C` on the same variable or
`record.field`, also when damlc compiles them to helpers that take the contract id. It
reports when `C` is consuming, is not `Archive`, returns a `ContractId` of the same template
(also inside a list, `Optional` or tuple), and `x` is mentioned after the exercise. The doc's
rule also covers `Archive`; it is left out because fetch, archive, then use is how contracts
are merged and is correct. A fetch through a wrapper that does more than fetch, such as
Splice's `fetchChecked`, is not recognised, and values derived from `x` before the exercise
are not followed.

**Results on real code:** no findings on `splice-amulet`, `splice-wallet-payments` or
`splice-util`.

**Recommendation:** fetch the successor contract id the choice returns, or compute the new
values before the exercise.
