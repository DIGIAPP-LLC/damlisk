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
$ damlisk scan examples/vulnerable/boolean-cst/boolean-cst.dar
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
