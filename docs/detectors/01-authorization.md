# Authorization detectors

Who may run a choice and whose authority it passes on.

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`controller-from-argument`](#controller-from-argument) | High | Medium | Consuming choice controlled only by an unchecked argument party |
| [`hardcoded-party`](#hardcoded-party) | Medium | High | Party identity built from or compared with a text literal |
| [`unprotected-archive`](#unprotected-archive) | High | Medium | Consuming choice controlled by a non-signatory |
| [`over-disclosure`](#over-disclosure) | Medium | Medium | Choice observers taken from the choice argument |
| [`delegated-authority-leak`](#delegated-authority-leak) | High | Medium | Non-signatory controller passes parties or amounts into a create or exercise |

## controller-from-argument

**Controller taken from the choice argument.** It reports a consuming
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

## hardcoded-party

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

## unprotected-archive

**Archive by a non-signatory.** It reports a consuming choice whose controllers are contract
parties none of which is a signatory.

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

## over-disclosure

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

## delegated-authority-leak

**Non-signatory controller passes parties or amounts into a create or exercise.** It reports
a choice whose controller is not a signatory of the contract, when the choice creates or
exercises with `Party`, `Numeric` or `Int` fields of the choice argument (also inside a list
or `Optional`) and the same action also carries contract data other than the controller's
own fields (a signatory party, or a contract id the signatories stored).

**Impact:** a choice body runs with the authority of the signatories and the controllers.
When the controller picks the parties or amounts, the controller makes the signatories sign
any contract or exercise they choose, such as minting tokens of any amount.

**Example** (`examples/vulnerable/delegated-authority-leak/daml/Main.daml`):

```haskell
template IssueRight
  with
    issuer : Party
    holder : Party
    rules : ContractId Rules
  where
    signatory issuer
    observer holder

    nonconsuming choice Mint : ContractId Token
      with
        value : Decimal
      controller holder
      do create Token with issuer; owner = holder; amount = value

    choice Grant : ContractId Token
      with
        payee : Party
      controller holder
      do create Token with issuer; owner = payee; amount = 10.0

    nonconsuming choice Forward : ContractId Token
      with
        payee : Party
        value : Decimal
      controller holder
      do exercise rules Pay with payee; value
```

```
$ damlisk scan examples/vulnerable/delegated-authority-leak/delegated-authority-leak.dar --detect delegated-authority-leak
[High] delegated-authority-leak Main.daml:53
    Main:IssueRight.Forward: argument `payee`, `value` used with the signatories' authority
[High] delegated-authority-leak Main.daml:47
    Main:IssueRight.Grant: argument `payee` used with the signatories' authority
[High] delegated-authority-leak Main.daml:41
    Main:IssueRight.Mint: argument `value` used with the signatories' authority
[High] delegated-authority-leak Main.daml:84
    Main:IssueRight.Request: argument `value` used with the signatories' authority
4 finding(s).
```

`Claim` (no argument), `Reissue` (controlled by the signatory `issuer`), `Capped` (`value`
bounded by `assertMsg`), `Memo` (creates a `Note` signed only by the controller), `Redeem`
(`value` is checked by the `ensure` of `Voucher`, `note` is `Text`), `Book` (creates a
`Ticket` the holder co-signs), `Spend` (exercises `Rules.Charge` with `spender = holder`, so
the holder acts on their own behalf), `Rules.Pay` and `Rules.Charge` (controlled by their
signatory) are not reported. In `Request` the controller
`requester` comes from the argument; only `value` is reported, since a party naming itself
is not a leak.

**How it works:** the detector traces the choice argument and the contract through the choice
body, following package helpers, and collects the fields that reach a created record, an
exercised contract id or an exercise argument (template and interface). Only parties and
amounts are reported, as the check targets; text, contract ids and records are not.
Arguments compared or bounded in the choice (`==`, `elem`, `<=`, ...), arguments used as
controllers, and arguments whose name matches a field read by the `ensure` of a template the
choice creates are dropped. A create is skipped when a controller field has the name of a
signatory field of the created template (the controller signs it too, as in a transfer
command), and an exercise is skipped when the controller is passed into it (the controller
acts on their own behalf, as when paying through a preapproval). Checks made inside an exercised choice of another template, or
through helpers that return `Either`, are not seen.

**Results on real code:** `splice-amulet` 0.1.24 and 0.1.19 have 1 finding,
`AmuletRules_AllocateDevelopmentFundCoupon`: the configured fund manager picks the
`beneficiary` of a DSO-signed coupon (the `amount` is checked). This is a designed delegation
to review, not a confirmed bug. 0.1.14, the token-standard API packages and
`splice-wallet-payments` have none.

**Recommendation:** take parties and amounts from contract fields the signatories agreed to,
bound and check every argument before it is used (`assertMsg`, `ensure`), or make a
signatory the controller.
