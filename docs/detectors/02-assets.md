# Assets detectors

Assets that can be stolen, given away or locked forever.

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`stuck-asset`](#stuck-asset) | Medium | Medium | Asset its owner cannot move: no owner-controlled consuming choice |
| [`value-to-arbitrary-party`](#value-to-arbitrary-party) | High | Medium | Asset created for an owner from the choice argument by a non-owner controller |

## stuck-asset

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

## value-to-arbitrary-party

**Asset created for an owner from the choice argument by a non-owner controller.** It reports
a choice that builds a template with an `owner` or `holder` field, sets that field from the
choice argument, and is controlled by a party that neither holds nor signs the current
contract.

**Impact:** a party with no claim on the asset decides who receives it. Anyone who can
exercise the choice moves the asset to any party or mints it for one.

**Example** (`examples/vulnerable/value-to-arbitrary-party/daml/Main.daml`):

```haskell
template Asset
  with
    issuer : Party
    owner : Party
    auditor : Party
    allowed : [Party]
    memo : Text
  where
    signatory issuer
    observer owner, auditor, allowed

    choice Transfer : ContractId Asset
      with
        requester : Party
        newOwner : Party
      controller requester
      do create this with owner = newOwner

    choice OwnerMove : ContractId Asset
      with
        newOwner : Party
      controller owner
      do create this with owner = newOwner
```

```text
$ damlisk scan examples/vulnerable/value-to-arbitrary-party/value-to-arbitrary-party.dar --detect value-to-arbitrary-party
[High] value-to-arbitrary-party Main.daml:24
    Main:Asset.Seize: argument `target` sets `owner` of the asset
[High] value-to-arbitrary-party Main.daml:30
    Main:Asset.Spread: argument `takers` sets `owner` of the asset
[High] value-to-arbitrary-party Main.daml:17
    Main:Asset.Transfer: argument `newOwner` sets `owner` of the asset
[High] value-to-arbitrary-party Main.daml:104
    Main:Factory.AgentMint: argument `receiver` sets `owner` of the asset
4 finding(s).
```

These choices are not reported:

- `OwnerMove` and `IssuerMove`: the controller holds or signs the contract.
- `CheckedMove` and `CheckedCaller`: the new owner or the argument controller is compared.
- `Claim`: the new owner is the controller, which
  [`controller-from-argument`](01-authorization.md#controller-from-argument) covers.
- `PaidMint`: the controller is passed into an exercise, so they pay from their own assets.
- `CopyOwner` and `Reissue`: the owner comes from a fetched contract or a contract field.
- `SetMemo` and `NoteFor`: no `owner` or `holder` field is set from the argument.

**How it works:** the detector traces the choice argument through the choice body, following
package helpers and callbacks such as `forA_`, and records what reaches each field of a record
built for a template. Building that record counts as the create, because damlc passes the
record to a generated helper that holds the `create`. A record copied whole from the argument
is not seen, and neither are fields named other than `owner` or `holder`. Any comparison of the
argument counts as a check, so `newOwner /= owner` hides a finding. Any exercise that receives
the controller counts as payment, even one that moves no value.

**Results on real code:** the Splice packages have no finding. `splice-amulet` 0.1.24 has four
choices that set `owner` of an `Amulet` from the argument. `AmuletRules_Mint` is controlled by
the signatory `dso`. `AmuletRules_Transfer`, `AmuletRules_BuyMemberTraffic` and
`TransferPreapproval_SendV2` compare their argument controller and pass it into an exercise.

**Recommendation:** make the current owner or a signatory the controller, or check the new
owner against parties stored on the contract.
