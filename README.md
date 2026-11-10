<div align="center">

<img src="docs/logo.svg" alt="damlisk" width="120">

# damlisk

**Static analyzer for Daml smart contracts.**

[![PyPI](https://img.shields.io/pypi/v/damlisk)](https://pypi.org/project/damlisk/)
[![CI](https://github.com/DIGIAPP-LLC/damlisk/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](setup.py)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)

[Detectors](#documentation) · [Examples](examples/vulnerable)

</div>

damlisk reads the Daml-LF inside a `.dar` through
[dazl](https://github.com/digital-asset/dazl-client), walks every template, choice and value,
and runs detectors over it. It needs no Daml source and no running ledger: what damlc
compiled is what gets checked.

## How it works

**1. Install damlisk** (Python 3.11 or newer):

```bash
pip install damlisk
```

**2. Build your Daml project** with `dpm build`. This choice uses a fetched value after its
contract was replaced:

```haskell
    nonconsuming choice PayOut : ContractId Receipt
      with
        cid : ContractId Account
      controller owner
      do
        acc <- fetch cid
        _ <- exercise cid Withdraw with amt = 10.0
        create Receipt with bank; owner; remaining = acc.amount
```

**3. Scan the DAR:**

```text
$ damlisk scan examples/vulnerable/stale-fetch/stale-fetch.dar --detect stale-fetch
[Medium] stale-fetch Main.daml:29
    Main:Desk.PayOut: `acc` is used after `Withdraw`
[Medium] stale-fetch Main.daml:38
    Main:Desk.PayTwice: `acc` is used after `Withdraw`
2 finding(s).
```

## Documentation

Each page explains its detectors: what they report, why it matters, an example with the
scan output, and how the check works and what it misses.

| # | Page | Detectors |
|---|---|---|
| 1 | [Authorization](docs/detectors/01-authorization.md) | `controller-from-argument`, `hardcoded-party`, `unprotected-archive`, `over-disclosure`, `delegated-authority-leak` |
| 2 | [Assets](docs/detectors/02-assets.md) | `stuck-asset`, `value-to-arbitrary-party` |
| 3 | [Contracts](docs/detectors/03-contracts.md) | `unsafe-primitive`, `untrusted-interface-exercise`, `stale-fetch` |
| 4 | [Validation](docs/detectors/04-validation.md) | `missing-amount-check`, `partial-function`, `nonconsuming-create`, `unchecked-fetch`, `time-from-argument`, `amount-tolerance`, `divide-before-multiply`, `unconsumed-input`, `hash-concat-collision`, `time-equality`, `missing-ensure`, `ignored-optional` |
| 5 | [Time](docs/detectors/05-time.md) | `time-dependence`, `weak-randomness` |
| 6 | [Loops](docs/detectors/06-loops.md) | `ledger-op-in-loop`, `unbounded-input-loop` |
| 7 | [Hygiene](docs/detectors/07-hygiene.md) | `boolean-cst`, `boolean-equal`, `unused-template-field`, `discarded-update`, `aborting-choice`, `tautological-compare`, `debug-trace`, `rtlo` |
| 8 | [Upgrade](docs/detectors/08-upgrade.md) | `sdk-version` |

<details>
<summary><b>All detectors</b> with impact and confidence</summary>

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`boolean-cst`](docs/detectors/07-hygiene.md#boolean-cst) | Medium | Medium | Boolean constants used as conditions |
| [`boolean-equal`](docs/detectors/07-hygiene.md#boolean-equal) | Informational | High | Comparison to `True` / `False` |
| [`controller-from-argument`](docs/detectors/01-authorization.md#controller-from-argument) | High | Medium | Consuming choice controlled only by an unchecked argument party |
| [`missing-amount-check`](docs/detectors/04-validation.md#missing-amount-check) | Low | Medium | `Decimal` template field not constrained by `ensure` |
| [`unused-template-field`](docs/detectors/07-hygiene.md#unused-template-field) | Informational | Medium | Template field that no ledger code reads |
| [`hardcoded-party`](docs/detectors/01-authorization.md#hardcoded-party) | Medium | High | Party identity built from or compared with a text literal |
| [`partial-function`](docs/detectors/04-validation.md#partial-function) | Low | Medium | Choice argument passed to `head`, `fromSome`, `!!`, ... |
| [`discarded-update`](docs/detectors/07-hygiene.md#discarded-update) | Medium | High | Ledger actions wrapped in `pure` and never run |
| [`nonconsuming-create`](docs/detectors/04-validation.md#nonconsuming-create) | High | Medium | Nonconsuming choice creates its own template without archiving `self` |
| [`unchecked-fetch`](docs/detectors/04-validation.md#unchecked-fetch) | High | Medium | Contract fetched from a choice argument and used without validation |
| [`time-from-argument`](docs/detectors/04-validation.md#time-from-argument) | Medium | Medium | Deadline logic on a caller-supplied `Time` instead of ledger time |
| [`amount-tolerance`](docs/detectors/04-validation.md#amount-tolerance) | Medium | High | `Decimal` amounts compared with `abs (a - b) < eps` instead of exactly |
| [`divide-before-multiply`](docs/detectors/04-validation.md#divide-before-multiply) | Medium | Medium | Result of a division multiplied, compounding its rounding error |
| [`unconsumed-input`](docs/detectors/04-validation.md#unconsumed-input) | High | Medium | Input contract of the same template read but not archived |
| [`aborting-choice`](docs/detectors/07-hygiene.md#aborting-choice) | Informational | High | Choice whose body always aborts |
| [`hash-concat-collision`](docs/detectors/04-validation.md#hash-concat-collision) | Medium | Medium | `sha256` of texts joined without a separator |
| [`time-equality`](docs/detectors/04-validation.md#time-equality) | Medium | High | Ledger time compared with `==` or `/=` |
| [`tautological-compare`](docs/detectors/07-hygiene.md#tautological-compare) | Medium | High | Value compared with itself (`payer == payer`) |
| [`unprotected-archive`](docs/detectors/01-authorization.md#unprotected-archive) | High | Medium | Consuming choice controlled by a non-signatory |
| [`missing-ensure`](docs/detectors/04-validation.md#missing-ensure) | Medium | High | Template with amount or time fields and no or trivial `ensure` |
| [`over-disclosure`](docs/detectors/01-authorization.md#over-disclosure) | Medium | Medium | Choice observers taken from the choice argument |
| [`unsafe-primitive`](docs/detectors/03-contracts.md#unsafe-primitive) | High | High | Unchecked cast of a contract id, interface or `Any` value |
| [`debug-trace`](docs/detectors/07-hygiene.md#debug-trace) | Informational | High | Debug trace left in production code |
| [`stuck-asset`](docs/detectors/02-assets.md#stuck-asset) | Medium | Medium | Asset its owner cannot move: no owner-controlled consuming choice |
| [`sdk-version`](docs/detectors/08-upgrade.md#sdk-version) | Informational | High | DAR built for a Daml-LF 1.x target |
| [`rtlo`](docs/detectors/07-hygiene.md#rtlo) | High | High | Bidirectional control character (right-to-left override) in source or `Text` |
| [`delegated-authority-leak`](docs/detectors/01-authorization.md#delegated-authority-leak) | High | Medium | Non-signatory controller passes parties or amounts into a create or exercise |
| [`untrusted-interface-exercise`](docs/detectors/03-contracts.md#untrusted-interface-exercise) | High | Medium | Interface contract id from the choice argument is exercised or fetched |
| [`value-to-arbitrary-party`](docs/detectors/02-assets.md#value-to-arbitrary-party) | High | Medium | Asset created for an owner from the choice argument by a non-owner controller |
| [`time-dependence`](docs/detectors/05-time.md#time-dependence) | Low | Medium | Ledger time decides a branch |
| [`weak-randomness`](docs/detectors/05-time.md#weak-randomness) | High | Medium | Ledger time or a hash picks a list element or map entry |
| [`ledger-op-in-loop`](docs/detectors/06-loops.md#ledger-op-in-loop) | Low | Medium | Create, exercise or fetch inside a loop |
| [`unbounded-input-loop`](docs/detectors/06-loops.md#unbounded-input-loop) | Medium | Medium | Loop over a list from the choice argument with no length check |
| [`stale-fetch`](docs/detectors/03-contracts.md#stale-fetch) | Medium | Medium | Fetched value used after the contract was replaced by a successor |
| [`ignored-optional`](docs/detectors/04-validation.md#ignored-optional) | Medium | Medium | `Optional` result discarded or forced with `fromSome` |

</details>

## Commands

```bash
damlisk --help                       # top-level usage and command list
damlisk --version                    # installed version
damlisk list-detectors               # every detector with impact and confidence
damlisk info path/to/project.dar     # packages, Daml-LF versions and declarations
damlisk scan path/to/project.dar     # run all detectors on the main package
damlisk report examples/dars --name digitalasset   # Markdown report for many DARs
```

`report` takes DAR files and folders (searched recursively) and writes a summary page with
one row per DAR, linking to a page with that DAR's findings:

```text
reports/digitalasset/report-2026-11-10.md
reports/digitalasset/report-2026-11-10/splice-amulet-0.1.24.md
```

It also takes `--out` (default `reports`), `--date` (default today), `--detect` and `--exclude`.

`scan` options:

| Option | Meaning |
|---|---|
| `--detect a,b` | Run only these detectors |
| `--exclude a,b` | Skip these detectors |
| `--json` / `--pretty-json` | Print findings as JSON |
| `--fail-on <impact>` | Exit with code 1 on a finding of this impact or higher (`high`, `medium`, `low`, `informational`, `none`) |
| `--traceback` | Show a Python traceback on error |

## Examples

[`examples/vulnerable/`](examples/vulnerable) has one small Daml project per detector. Each
holds the cases that are reported and the look-alikes that are not. `examples/dars/` holds the
Splice DARs used as a real-world baseline in the tests. No DAR is committed: `make dars`
builds every example with `dpm build` and downloads every published Splice version from the
official [Splice repository](https://github.com/canton-network/splice/tree/main/daml/dars).

## Local development

```bash
python -m venv .venv
source .venv/bin/activate
make dev-init        # editable install with the dev dependency group
make dars            # build the example DARs and download the Splice DARs (needs dpm)
```

Run the tests and linters, and build the wheel:

```bash
make test            # pytest
make lint            # mypy, black, flake8, isort
make build           # dist/damlisk-<version>-py3-none-any.whl
```

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) is started by hand from the Actions
tab (**Run workflow**). It runs the same steps inside the Nix dev shell from
[`flake.nix`](flake.nix): it installs dpm and the Daml SDK, runs `make dars`, then lint and
tests. Run it locally with:

```bash
nix develop --command make ci
```

## Publishing to PyPI

Pushing a `v*.*.*` tag runs [`.github/workflows/workflow.yml`](.github/workflows/workflow.yml).
It first runs the CI workflow (DAR builds, lint, tests); only if that passes does it build
the sdist and wheel with the tag as the version (`v0.2.0` gives `damlisk --version`
= `0.2.0`), checks that, and uploads to PyPI through trusted publishing, so no API token is
stored in the repository:

```bash
git tag v0.2.0
git push origin v0.2.0
```

## License

damlisk is licensed under the [Apache License, Version 2.0](LICENSE).

Copyright 2026 DIGIAPP LLC.
