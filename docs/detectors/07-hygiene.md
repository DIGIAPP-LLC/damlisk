# Hygiene detectors

Dead code, constant conditions, debug output and hidden characters.

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`boolean-cst`](#boolean-cst) | Medium | Medium | Boolean constants used as conditions |
| [`boolean-equal`](#boolean-equal) | Informational | High | Comparison to `True` / `False` |
| [`unused-template-field`](#unused-template-field) | Informational | Medium | Template field that no ledger code reads |
| [`discarded-update`](#discarded-update) | Medium | High | Ledger actions wrapped in `pure` and never run |
| [`aborting-choice`](#aborting-choice) | Informational | High | Choice whose body always aborts |
| [`tautological-compare`](#tautological-compare) | Medium | High | Value compared with itself (`payer == payer`) |
| [`debug-trace`](#debug-trace) | Informational | High | Debug trace left in production code |
| [`rtlo`](#rtlo) | High | High | Bidirectional control character (right-to-left override) in source or `Text` |

## boolean-cst

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

## boolean-equal

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

## unused-template-field

**Unused template field.** It reports template fields that no
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

## discarded-update

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

## aborting-choice

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

## tautological-compare

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

## debug-trace

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

## rtlo

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
