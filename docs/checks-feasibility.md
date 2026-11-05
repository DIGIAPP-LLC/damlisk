# daml-scanner — Check Feasibility Analysis

Static analysis of Daml contracts from compiled `.dar` archives (Daml-LF), modelled on
Slither (detectors over an IR) and Mythril (symbolic execution with attacker models), using
`dazl` to decode Daml-LF and following the `damlforge` project layout.

Sources analysed:

| Repo | Path | Role |
|---|---|---|
| slither | `/Users/artem_bogomaz/Documents/GIT5/slither` | 102 registered detectors, 28 printers, data-dependency/taint |
| mythril | `/Users/artem_bogomaz/Documents/GIT5/mythril` | 17 detection modules, LASER symbolic VM, z3 |
| dazl-client | `dazl-client` | `dazl.damlast` Daml-LF decoder |
| damlforge | `damlforge` | target layout, DAR loader + LF2 patch (`forge/stubgen`) |
| splice | `splice` | real-world `daml.yaml` build options, `.dlint.yaml` (compiler/linter overlap evidence) |

---

## 0. Navigation map

Every path below exists and was checked. Section references show where in this document
each path is used.

### 0.1 Slither — `/Users/artem_bogomaz/Documents/GIT5/slither`

| What | Path | Used in |
|---|---|---|
| Entry / CLI, detector discovery, plugin loading | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/__main__.py` | §9 |
| Pipeline (compile → parse → analyze → run detectors) | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/slither.py` | §9 |
| Core model (declarations, CFG, source mapping) | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/core` | §9 |
| Result filtering, ignore comments, triage | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/core/slither_core.py` | §9 |
| CFG node | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/core/cfg/node.py` | §2 |
| SlithIR operations | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/slithir/operations` | §9 |
| SlithIR lowering heuristics | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/slithir/convert.py` | §9 |
| SSA | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/slithir/utils/ssa.py` | §2 |
| Expression → IR visitor | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/visitors/slithir/expression_to_slithir.py` | §9 |
| Data dependency / taint | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/analyses/data_dependency/data_dependency.py` | §8, §9 |
| Write-path analysis | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/analyses/write/are_variables_written.py` | §8 |
| `AbstractDetector` | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/detectors/abstract_detector.py` | §9 |
| Detector registry | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/detectors/all_detectors.py` | §4 |
| All detector sources (one folder per category) | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/detectors` | §4 |
| Reentrancy fixpoint base | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/detectors/reentrancy/reentrancy.py` | §4.5 |
| `AbstractPrinter`, printer registry | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/printers/abstract_printer.py`, `/Users/artem_bogomaz/Documents/GIT5/slither/slither/printers/all_printers.py` | §4.6 |
| `vars-and-auth` printer (model for the authorization matrix) | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/printers/functions/authorization.py` | §4.6 |
| Output (`Output`, JSON, SARIF, fingerprint) | `/Users/artem_bogomaz/Documents/GIT5/slither/slither/utils/output.py` | §9 |
| Plugin example (entry-point group) | `/Users/artem_bogomaz/Documents/GIT5/slither/plugin_example` | §9 |

### 0.2 Mythril — `/Users/artem_bogomaz/Documents/GIT5/mythril`

| What | Path | Used in |
|---|---|---|
| CLI | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/interfaces/cli.py` | §6 |
| Orchestrator (`fire_lasers`) | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/mythril/mythril_analyzer.py` | §6 |
| Symbolic execution wrapper (actors, strategies, hooks) | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/symbolic.py` | §6.3 |
| `DetectionModule` base | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/module/base.py` | §6.1 |
| Module loader / hook registration | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/module/loader.py`, `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/module/util.py` | §6.1 |
| **All 17 detection modules** | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/module/modules` | §6.2 |
| Deferred issues (`PotentialIssue`) | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/potential_issues.py` | §6.3 |
| Exploit sequence from z3 model | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/solver.py` | §6.1 |
| Issue collection, report, SWC registry | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/security.py`, `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/report.py`, `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/analysis/swc_data.py` | §6.3 |
| LASER VM (hooks, multi-tx loop) | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/laser/ethereum/svm.py` | §6.3 |
| World/global state, annotations | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/laser/ethereum/state` | §6.3 |
| Actors and symbolic transactions | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/laser/ethereum/transaction/symbolic.py` | §6.3 |
| Search strategies, bounded loops | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/laser/ethereum/strategy` | §6.3 |
| LASER plugins (pruners, coverage, summaries, …) | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/laser/plugin/plugins`, `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/laser/plugin/interface.py` | §6.3 |
| SMT wrapper, model/timeout | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/laser/smt`, `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/support/model.py` | §6.3 |
| Plugin discovery (entry points) | `/Users/artem_bogomaz/Documents/GIT5/mythril/mythril/plugin/discovery.py` | §9 |

### 0.3 dazl-client — `dazl-client`

| What | Path | Used in |
|---|---|---|
| Package metadata (dazl 8.9.0, deps) | `dazl-client/pyproject.toml` | §3.3 |
| `DarFile`, `CachedDarFile` | `dazl-client/python/dazl/damlast/pkgfile.py` | §3.1 |
| `parse_archive` (LF1/LF2 dispatch) | `dazl-client/python/dazl/damlast/parse.py` | §3.1 |
| LF1 parser | `dazl-client/python/dazl/damlast/parse_factory/pb_v1.py` | §3.3 |
| LF2 parser (builtin numbering, by-key bugs) | `dazl-client/python/dazl/damlast/parse_factory/pb_v2.py` | §3.3 |
| **Daml-LF AST model** (`Package`, `Module`, `DefTemplate`, `TemplateChoice`, `Expr`, `Update`, `BuiltinFunction`, `Location`) | `dazl-client/python/dazl/damlast/daml_lf_1.py` | §3 |
| Name lookup (`PackageLookup`, `MultiPackageLookup`) | `dazl-client/python/dazl/damlast/lookup.py` | §3.1 |
| Visitors (non-recursive) | `dazl-client/python/dazl/damlast/visitor.py` | §3.3 |
| Type/name helpers | `dazl-client/python/dazl/damlast/util.py` | §3 |
| Generated protobuf (`daml_lf_pb2`, `daml_lf1_pb2`, `daml_lf2_pb2`) | `dazl-client/python/dazl/_gen/com/digitalasset/daml/lf/archive` | §3.3 |
| Fixture DARs (SDK 0.13 → 2.9.1, LF1) | `dazl-client/_fixtures/archives` | §3.3 |
| Fixture DAR, LF2 | `dazl-client/_fixtures/archives/3.3.0/all-kinds-of-1.0.0_lf.dar` | §3.3 |
| Fixture Daml sources | `dazl-client/_fixtures/src` | §3.3 |
| LF2 parser tests | `dazl-client/python/tests/unit/test_pb_v2_parser.py` | §3.3 |

### 0.4 damlforge — `damlforge`

| What | Path | Used in |
|---|---|---|
| Packaging and tooling to copy | `damlforge/pyproject.toml`, `damlforge/setup.py`, `damlforge/setup.cfg`, `damlforge/Makefile`, `damlforge/quicktest.sh` | §10 |
| CI workflows | `damlforge/.github/workflows` | §10 |
| click CLI pattern | `damlforge/forge/cli/main.py` | §10 |
| Diagnostics model, error codes | `damlforge/forge/exceptions.py`, `damlforge/forge/models/error_codes.py` | §9 |
| IR (frozen dataclasses), lowering | `damlforge/forge/ir/nodes.py`, `damlforge/forge/ir/lower.py` | §10 |
| `check_*` structural rules (style to follow) | `damlforge/forge/semantics/analysis/structure.py` | §10 |
| **DAR loader** (`_read_dar`) | `damlforge/forge/stubgen/dar.py` | §3.1 |
| **LF2 parser patch** (`Parser23`) | `damlforge/forge/stubgen/lf2.py` | §3.3 |
| Party-reference walker over LF (`PartyRefs`) | `damlforge/forge/stubgen/parties.py` | §8.1 |
| LF field usage reference (templates, choices, keys, interfaces) | `damlforge/forge/stubgen/render.py` | §3 |
| LF2 test (with `importorskip("dazl")`) | `damlforge/tests/stubgen/test_lf2.py` | §10 |
| **Regression DARs** (Splice, LF 2.1) | `damlforge/examples/dars` | §3.2 |
| Daml semantics guide (rule rationale) | `damlforge/docs/guide` | §7 |
| Working Python env with dazl 8.9 | `damlforge/.venv` | §3.3 |

### 0.5 Splice — `splice`

| What | Path | Used in |
|---|---|---|
| dlint config (IDE-only, all hints disabled) | `splice/.dlint.yaml` | §5.1 |
| Example build options (`-Wunused-binds`, `--target=2.1`) | `splice/daml.yaml` | §5.1 |
| Daml sources of the DARs used for testing | `splice/daml` (e.g. `splice/daml/splice-amulet`) | §3.2 |
| Token-standard projects | `splice/token-standard` | §4.3 |

### 0.7 This project — `/Users/artem_bogomaz/Documents/GIT5/daml-scanner`

| What | Path |
|---|---|
| This document | `/Users/artem_bogomaz/Documents/GIT5/daml-scanner/docs/checks-feasibility.md` |
| Architecture UML | `/Users/artem_bogomaz/Documents/GIT5/daml-scanner/architecture.puml` |

---

## 1. Executive summary

* **The approach is viable.** `dazl` (8.9) + damlforge's `forge/stubgen/lf2.py` patch decodes
  real Splice DARs (Daml-LF **2.1**) into a full typed AST including choice bodies and update
  expressions. Verified on `examples/dars/splice-amulet-0.1.24.dar`: 22 modules, 34 templates,
  113 choices, 7 921 top-level values, 0 decode errors, ~0.7 s.
* **Slither's *method* transfers completely; its *rule list* only partly.** The pipeline
  (compiled artefact → IR → data-dependency/taint → detector classes with impact/confidence →
  JSON/SARIF) works on Daml-LF unchanged in spirit. Of 102 Slither rules, **36 apply to Daml**
  (8 PORT almost unchanged, 25 ADAPT as a Daml analogue, 3 BLOCKED on a dazl patch). The other
  **66 target constructs Daml does not have** (assembly, gas, storage slots, `delegatecall`,
  `msg.value`, unchecked low-level returns, fallback reentrancy, solc bugs, ERC events).
* **Compiler overlap has been checked.** None of the 36 applicable rules is fully covered by
  a damlc *error* (anything damlc rejects can never be inside a DAR). **6 overlap with
  damlc warnings, dlint or upgrade validation** — these are kept but downgraded, because
  warnings are opt-in or can be suppressed, dlint never runs in `daml build`/CI, and none of
  this is recorded in the DAR. See §5.
* **The valuable checks are Daml-native** and have no Slither/Mythril equivalent:
  authorization/controller analysis, delegated-authority leaks, unvalidated `ContractId`
  arguments, asset duplication via non-consuming choices, untrusted interface implementations,
  missing `ensure` invariants, and Smart Contract Upgrade (SCU) compatibility (§7).
* **Mythril: 13 of 17 modules apply** (2 PORT, 8 ADAPT, 3 weak ADAPT, 4 N/A: reentrancy
  ×2, unchecked return, arbitrary jump). All 13 have a static approximation; symbolic
  execution adds proof plus a Daml Script exploit (§6).
* **Mythril's engine is portable in concept, not in code.** Its attacker-actor model,
  deferred `PotentialIssue`s and multi-transaction exploration map well onto Daml
  (attacker party, active contract set as world state), but require writing a Daml-LF
  interpreter. Recommended as a later phase.
* **dazl has decoding gaps** that the scanner must patch (interface instances, exception
  definitions, LF2 builtin numbering, LF2 by-key updates). See §3.

---

## 2. Why Daml changes the picture

| EVM / Solidity concept | Daml-LF reality | Consequence for checks |
|---|---|---|
| Mutable storage | Immutable contracts; "update" = archive + create | No storage-layout, uninitialized-storage, write-after-write on state |
| `msg.sender` / `tx.origin` | Authorization by signatories, controllers, observers, checked by the engine | Access control becomes "who is controller, where does that party come from" |
| External calls, fallback, reentrancy | No callbacks; a consuming choice archives the contract *before* its body runs | Reentrancy family N/A; analogue is **exercising code of an untrusted interface implementation** |
| Return codes (`call`, `send`) | Any failure aborts the whole transaction atomically | Unchecked-return family N/A |
| uint256 wraparound | Int64 overflow **aborts**; Numeric has fixed scale | Overflow is a liveness (DoS) issue, not theft; precision loss on Numeric remains |
| Gas, loops, return-bomb | No gas; transaction size/time limits on the participant | Unbounded loops = DoS / oversized transaction |
| Ether balance | No native coin; assets are contracts (e.g. Splice `Holding`) | "Ether theft" → "attacker gains a holding / ownership" |
| Inheritance, modifiers | Interfaces + typeclasses (erased into dictionary records in LF) | Inheritance checks N/A; interface conformance checks instead |
| Assembly, compiler versions | Pure, typed functional core; LF version + SDK version | Assembly/compiler-bug detectors N/A; replace with SDK/LF-version policy |
| Public state | Sub-transaction privacy; data visible to stakeholders only | New class: **over-disclosure** via observers / choice observers |
| Contract keys | Present in LF 1.x; **absent in LF 2.1** (Splice: zero by-key updates found) | Key checks only for LF 1.x / LF 2.dev packages |

Useful property: Daml-LF is already **SSA-like** (immutable `let` bindings, no
reassignment), so Slither's SSA/phi machinery is unnecessary; data dependency is a plain
walk over `let`/`abs`/`app` binders.

---

## 3. Input layer: what dazl gives us

### 3.1 Loading

```python
from dazl.damlast.pkgfile import DarFile          # .archives(), .sdk_version(), .manifest()
from dazl.damlast.lookup import MultiPackageLookup  # .search("pkg:Mod.Name:Entity")
from dazl.damlast import daml_lf_1 as lf          # single AST model for LF1 and LF2
```

`forge/stubgen/dar.py::_read_dar` (damlforge) already: reads `Main-Dalf` from the manifest,
installs the LF2 patch, returns `(main_archive, all_archives, daml_sources_by_module)`.
The embedded `.daml` sources are available, which enables source snippets and
`-- daml-scanner-disable-next-line` style suppression comments.

### 3.2 Census of a real package (verified)

`splice-amulet-0.1.24.dar`, main package only, all values forced:

| Node | Count | Node | Count |
|---|---|---|---|
| `Expr.val` (ref to top-level value) | 11 850 | `Update.exercise` | 162 |
| `Expr.app` | 9 288 | `Update.create` | 75 |
| `Expr.rec_proj` | 5 058 | `Update.fetch` | 34 |
| `Expr.struct_con` (typeclass dictionaries) | 2 518 | `Update.block` / `pure` | 225 / 222 |
| `Expr.builtin` | 1 316 | `Expr.throw` | 34 |
| `Expr.let` / `Expr.case` | 1 121 / 753 | `Expr.to_interface` / `from_interface` | 23 / 24 |

Observations that shape the design:

1. **Template and choice fields are thin wrappers.** `signatories` is
   `App(val '$$csignatory2', [this])`; a choice `update` is
   `App(val '$$$$sc_AmuletRules_5', [self, this, arg])`. Every analysis needs a
   **ValName → DefValue index across all packages in the DAR** and inlining/summaries.
2. **Typeclass dictionaries are records of closures** (`struct_con`, `struct_proj`). Calls
   through `Action`/`Foldable`/`HasCreate` etc. are higher-order; precise call resolution
   needs dictionary resolution (known dictionary values are top-level `$f...` values, so
   this is tractable for the common cases).
3. **Many ledger ops live in other packages** (`daml-stdlib`, `splice-util`): e.g. no
   `get_time` occurs in the amulet package itself. Whole-DAR analysis is mandatory.
4. `DefValue.expr` is **lazy**; parse errors surface on first access.

### 3.3 What is decoded / what is not

| Construct | Status | Notes |
|---|---|---|
| Template: `param`, `signatories`, `observers`, `precond` (ensure), `choices`, `location` | ✅ | |
| Template `key` (`type`, `complex_key`, `maintainers`) | ✅ LF1 / ⚠ LF2 | LF2 only `complex_key` |
| Template `implements` (interface instances) | ❌ | Not decoded — blocks interface-conformance checks; must patch parser |
| Choice: `name`, `consuming`, `controllers`, `observers`, `authorizers`, `arg_binder`, `self_binder`, `ret_type`, `update`, `location` | ✅ | `Archive` choice may have 0 range |
| Interface: `methods` (types), `choices`, `view` (type), `requires`, `param` | ⚠ | No method **bodies**, no `location`, no co-implements |
| `DefException` | ❌ | Only visible as a `DefDataType` record |
| Data types, type synonyms, values | ✅ | |
| Expr: all cases incl. interface ops, `throw`, `to/from_any` | ✅ | `Expr.Sum_match` buggy for `choice_observer` — dispatch on `_Sum_name` |
| Update: `create`, `exercise`, `fetch`, `get_time`, `embed_expr`, `try_catch`, `*_interface`, `ledger_time_lt` | ✅ | `exercise_by_key`/`try_catch` lack properties; use `_Sum_name`/`_Sum_value` |
| LF2 `lookup_by_key` / `fetch_by_key` | ⚠ | key expression dropped; `query_n_by_key` unhandled |
| LF2 builtins | ⚠ | dazl maps with LF1 numbering. With the damlforge patch values come back as raw ints; decode with `daml_lf2_pb2.BuiltinFunction.Name(n)` (verified: 1=`ERROR`, 7=`ADD_INT64`, 34=`APPEND_TEXT`) |
| LF2 builtin **types** | ⚠ | Same numbering bug (`DATE`→`DECIMAL`) |
| Source locations | ✅ | `Location(module, range)` on templates, choices, values, data types, some exprs; **0-based** lines; module → `daml/A/B/C.daml` |
| Visitors | ⚠ | `ExprVisitor` does not recurse, no Update visitor; write our own walker |

Environment note: the dazl-client repo `.venv` cannot `import dazl` (protobuf 7 generated
code vs protobuf 6 runtime, grpcio too old). damlforge's `.venv` (dazl 8.9 from PyPI) works.
Depend on `dazl>=8.9` and vendor/extend `lf2.py` inside the scanner.

---

## 4. Slither detectors → Daml

### 4.0 How to read this section

Slither's value is two separate things:

1. **The method** — compiled artefact → IR → data-dependency/taint → detector classes with
   impact/confidence → JSON/SARIF/fingerprints. This transfers **completely**; Daml-LF has
   everything it needs (templates, choices, signatories, controllers, typed expressions,
   create/exercise/fetch).
2. **The rule list** — each rule targets a specific bug class. A rule only transfers if the
   bug class can exist in Daml.

Verdicts:

* **PORT** — same rule, Daml syntax.
* **ADAPT** — same intent, Daml-specific semantics.
* **BLOCKED** — feasible after a dazl parser patch (§3.3).
* **N/A** — the construct does not exist in Daml, or damlc rejects it (so it can never be
  in a DAR).

The "Compiler" column says whether damlc / dlint / upgrade validation already reports the
issue; details and the decision for each overlap are in §5.

* `—` no overlap · `W` damlc warning (opt-in or suppressible) · `L` dlint (IDE only) ·
  `U` upgrade validation (damlc `upgrades:` / participant upload) · `E` damlc error.

### 4.1 Applicable rules — PORT (8)

| # | Slither | Daml check | Daml example that fires | Daml-LF match | Compiler |
|---|---|---|---|---|---|
| 1 | boolean-equal | `boolean-equal` | `if approved == True then …` | `EQUAL` builtin with `prim_con True/False` operand | L |
| 2 | boolean-cst | `boolean-cst` | `if True then …`, `ok \|\| True` | `case` on / `\|\|` with a `prim_con` Bool | L |
| 3 | tautological-compare | `tautological-compare` | `ensure amount >= amount` | comparison builtin with α-equal operands | — |
| 4 | tautology | `tautology` | `ensure (count : Int) <= 9223372036854775807` | comparison against type bounds of Int64 / Numeric scale | — (damlc only rejects out-of-range *literals*) |
| 5 | redundant-statements | `redundant-statements` | `let unused = amount * 2.0` / `pure ()` with no effect | `let` binder with no reference; `Update.pure` of unit in a `block` | W (`-Wunused-binds`, opt-in) |
| 7 | cyclomatic-complexity | `cyclomatic-complexity` | choice body with > 11 branches | count `case` alternatives + `if` per choice (after inlining) | — |
| 10 | rtlo | `rtlo` | `-- ‮ hidden text` in source or a `Text` literal | U+202E/bidi chars in embedded `.daml` and `PrimLit.text` | — |
| 11 | backdoor | `suspicious-name` | choice named `Backdoor`, `AdminOverride`, `Debug` | template/choice name list | — |

### 4.2 Applicable rules — ADAPT (25)

| # | Slither | Daml check | Daml example that fires | Daml-LF match | Compiler |
|---|---|---|---|---|---|
| 12 | suicidal | `unprotected-archive` | see example A | `choice.consuming` and controllers ∉ signatories | — |
| 13 | arbitrary-send-eth | `value-to-arbitrary-party` | see example B | create of asset template whose owner field ← choice arg, controller ≠ owner | — |
| 14 | arbitrary-send-erc20 | `delegated-transfer-arbitrary-owner` | choice consumes a `Holding` whose owner is not tied to the controller and recreates it for `newOwner` | fetch/exercise on cid from arg + create with owner from arg | — |
| 15 | arbitrary-send-erc20-permit | `unbounded-preapproval` | `TransferPreapproval`-like contract usable repeatedly, no amount / expiry | non-consuming choice on approval contract, no time/amount guard | — |
| 16 | tx-origin | `controller-from-argument` | see example B (`controller requester`) | controllers expression reads `arg` instead of `this` | — |
| 17 | missing-zero-check | `missing-amount-check` | see example C | `Numeric` field, `precond` absent / `True`; amount arg used without `> 0` | — |
| 18 | divide-before-multiply | `divide-before-multiply` | `fee = (amount / 100.0) * rate` | `DIV_NUMERIC` result feeding `MUL_NUMERIC`; `DIV_INT64` truncation | — |
| 19 | incorrect-equality | `incorrect-equality` | `when (balance == 0.0) …`, `now == deadline` | `EQUAL` on Numeric / Time operands | — |
| 20 | timestamp | `time-dependence` | `now <- getTime; if now == deadline then …` | `Update.get_time` / `ledger_time_lt` flowing into `case` condition | — |
| 21 | weak-prng | `weak-randomness` | `players !! (toInt now % n)` | `get_time` or `SHA256_TEXT` of ledger data flowing into index / selection | — |
| 22 | encode-packed-collision | `hash-concat-collision` | `sha256 (a <> b)` — `"ab"<>"c"` == `"a"<>"bc"` | `SHA256_TEXT` over `APPEND_TEXT` of ≥2 variable fields without separator | — |
| 23 | calls-loop | `ledger-op-in-loop` | see example D | `create`/`exercise`/`fetch` inside `foldl`/`forA`/`mapA` closure | — |
| 24 | costly-loop | `ledger-op-in-loop` (creates) | `forA_ items \i -> create Item with …` | `create` inside fold closure | — |
| 25 | controlled-array-length | `unbounded-input-loop` | see example D (`payees` unbounded) | list from choice `arg` is fold source, no length guard | — |
| 26 | controlled-delegatecall | `untrusted-interface-exercise` | see example E | `exercise_interface` / `fetch_interface` on cid from `arg` | — |
| 27 | reentrancy-balance | `stale-fetch` | `h <- fetch cid; exercise cid Archive; create … with amount = h.amount + x` | value from `fetch` used after consuming exercise on the same cid | — |
| 28 | unused-return | `ignored-optional` | `r <- lookupByKey @T k; …` with `r` unused, or `fromSome r` | `Optional` result discarded or forced via `fromSome` | W (`-Wunused-matches` covers only unused pattern vars, opt-in) |
| 29 | low-level-calls | `unsafe-primitive` | `coerceContractId cid`, `unsafeFromInterface` | `COERCE_CONTRACT_ID`, `unsafe_from_interface`, `from_any` | — |
| 30 | locked-ether | `stuck-asset` | `Holding` with only `Archive` and issuer-controlled choices; owner cannot transfer | no consuming choice controlled by owner/holder field except `Archive` | — |
| 31 | suicidal (inverse) / protected-vars | `annotated-controller` | `-- @security controller=issuer` above a choice, but controller is `owner` | comments in embedded source vs IR controllers | — |
| 32 | unprotected-upgrade | `scu-incompatible` | v2 adds non-`Optional` field, removes a choice, changes signatories | diff of two DARs' templates/choices/data types | U (only if configured; see §5) |
| 33 | deprecated-standards | `deprecated-feature` | exceptions (`throw`/`try`) in LF2, LF1-only features, deprecated stdlib | `Expr.throw`, `try_catch`, deprecated `val` targets | W (`-Wdeprecated-exceptions`, suppressible) |
| 35 | solc-version | `sdk-version` | DAR built with an SDK with a known defect, or LF 1.x target | manifest `Sdk-Version`, LF version | — |
| 36 | write-after-write | `write-after-write` | `this with amount = a, amount = b`; `create` then immediate `archive` of the result | duplicate field in `rec_upd`; create→exercise `Archive` on the returned cid | — |
| 37 | unused-state | `unused-template-field` | template field never read by signatory/observer/ensure/choice/view | template field with no `rec_proj` anywhere | — |

Slither's whole `compiler_bugs/` category (8 solc defects, §4.5) is not ported rule by rule; its intent is covered by `sdk-version` driven by a list of known damlc / engine defects per SDK version.

### 4.3 Applicable rules — BLOCKED until dazl patch (3)

| # | Slither | Daml check | Daml example | Needs |
|---|---|---|---|---|
| 38 | missing-inheritance | `missing-interface-instance` | template has `owner`, `amount`, `instrument` but no `interface instance Holding` | `implements` decoding |
| 39 | erc20-interface | `token-standard-conformance` | `Holding` view returns `owner` ≠ the contract's real owner field | `implements` + interface instance method bodies |
| 40 | erc721-interface | `token-standard-conformance` (allocations / transfer factories) | `TransferFactory` implementation ignores `expectedAdmin` | same |

### 4.4 Worked Daml examples

**A — `unprotected-archive`** (Slither `suicidal`): a non-signatory can destroy the contract.

```daml
template Asset with issuer : Party; owner : Party; auditor : Party
  where
    signatory issuer
    observer owner, auditor
    choice Cancel : ()
      controller auditor
      do pure ()
```

LF: `choice.consuming == True`, `controllers = rec_proj this auditor`, `auditor` not in
`signatories`.

**B — `controller-from-argument` / `value-to-arbitrary-party`** (Slither `tx-origin`,
`arbitrary-send-eth`): anyone who can see the contract can move it.

```daml
    choice Transfer : ContractId Asset
      with requester : Party; newOwner : Party
      controller requester
      do create this with owner = newOwner
```

LF: controllers expression is `rec_proj arg requester`; create's `owner` ← `arg.newOwner`.

**C — `missing-amount-check`** (Slither `missing-zero-check`):

```daml
template Holding with owner : Party; amount : Decimal
  where signatory owner
```

LF: `precond` is `None`/`True`, template has a `Numeric` field.

**D — `ledger-op-in-loop` / `unbounded-input-loop`** (Slither `calls-loop`,
`controlled-array-length`): exceeds transaction limits, one failure blocks all.

```daml
    choice PayAll : ()
      with payees : [(Party, Decimal)]
      controller owner
      do forA_ payees \(p, a) -> exercise cashCid Pay with to = p; amt = a
```

**E — `untrusted-interface-exercise`** (Slither `controlled-delegatecall`):

```daml
    choice Settle : ()
      with holdingCid : ContractId Holding
      controller owner
      do exercise holdingCid Transfer with newOwner = receiver
```

`Holding` is an interface; the implementation behind `holdingCid` can come from any
package the participant vetted and runs with the authority of `owner` + this contract's
signatories.

### 4.5 Not applicable (66)

| Slither rules | Count | Reason |
|---|---|---|
| reentrancy-eth, reentrancy-no-eth, reentrancy-benign, reentrancy-events, reentrancy-unlimited-gas | 5 | No callbacks; consuming choice archives before its body runs (analogue: #26) |
| incorrect-return, return-leave, incorrect-shift, constant-function-asm, assembly | 5 | No assembly |
| array-by-reference, enum-conversion, multiple-constructors, public-mappings-nested, reused-constructor, abiencoderv2-array, storage-array, uninitialized-fptr-cst | 8 | solc defects (intent covered by `sdk-version`, #35) |
| unchecked-lowlevel, unchecked-send, unchecked-transfer, return-bomb | 4 | Failures abort atomically; no gas |
| msg-value-loop, msg-value-in-nonpayable, delegatecall-loop, cache-array-length, external-function, var-read-using-this, domain-separator-collision, incorrect-exp | 8 | EVM-only concepts (`EXP_INT64` is explicit, no `^`/`**` confusion) |
| unindexed-event-address, erc20-indexed, events-access, events-maths | 4 | No events; the transaction tree is the event log |
| chainlink-feed-registry, gelato-unprotected-randomness, optimism-deprecation, out-of-order-retryable, pyth-deprecated-functions, pyth-unchecked-confidence, pyth-unchecked-publishtime, chronicle-unchecked-price | 8 | Vendor/L2 specific |
| constable-states, immutable-states, function-init-state, uninitialized-local, uninitialized-state, uninitialized-storage, mapping-deletion | 7 | Immutable records, every value initialised — **damlc error** if not (E) |
| shadowing-abstract, shadowing-builtin, shadowing-local, shadowing-state, variable-scope | 5 | Names resolved and erased before LF — **not visible in a DAR**; GHC `-Wname-shadowing` is the place for it |
| pragma | 1 | Mixed LF versions — **damlc error**: "Targeted LF version 2.1 but dependencies have incompatible LF versions"; a DAR records a single `Sdk-Version`, so mixed SDKs are not visible |
| naming-convention | 1 | Capitalisation and clashing names are **damlc errors** ("Multiple declarations of 'Transfer'"); what remains (Splice `Template_Choice` prefix) is style only, followed by all 271 Splice choices |
| name-reused | 1 | **damlc error** "Ambiguous module name" for duplicate modules in dependencies; unused duplicates are dropped from the DAR; only deliberate package-qualified imports (`import "pkg" M`) put two `M:T` in one DAR |
| dead-code | 1 | Not decidable from a DAR: top-level values are the package's API for other packages (Daml-LF has no `private`/`internal`), and templates are created by Ledger API commands, not only by Daml code |
| **Total** | **66** | 66 N/A + 36 applicable = 102 registered Slither detectors. Unregistered `token-reentrancy` (N/A) and `unused-import` (erased in LF; the package-level variant "unused DAR dependency" is feasible) are not counted. |
| constant-function-state | 1 | Purity enforced by the type system (`Update` vs pure) — **damlc error** (E) |
| unimplemented-functions | 1 | Missing interface method implementation — **damlc error** (E) |
| incorrect-modifier, void-cst, assert-state-change, incorrect-using-for, incorrect-unary, too-many-digits | 6 | Solidity syntax specifics (`too-many-digits` could be a trivial Numeric-literal readability check) |

### 4.6 Printers

| Printer | Verdict | Daml version |
|---|---|---|
| vars-and-auth | ADAPT — **highest value** | **Authorization matrix**: template × choice × controllers × consuming × effects × parties whose authority is used |
| call-graph, cfg | ADAPT | Value call graph (through dictionaries); per-choice **effect tree** (create/exercise/fetch with path conditions) |
| contract-summary, function-summary, entry-points, declaration, data-dependency, require, human-summary, loc, ck, halstead, martin, slithir | PORT | Same idea over templates/choices/IR (`require` → ensure + assert/abort sites) |
| inheritance, inheritance-graph | BLOCKED | Interface-implementation graph needs `implements` |
| echidna | ADAPT | Guidance for Daml Script fuzzing (parties, choice arg types, constants) |
| not-pausable | ADAPT | Choices not guarded by an operator/DSO "paused" config |
| c3-linearization, constructor-calls, cheatcode, evm, function-id, variable-order, dominator, modifiers | N/A | |

---

## 5. Compiler, linter and runtime overlap

The scanner works on a **DAR**, i.e. on code that damlc already accepted. Four layers can
already report something; each was checked against the 36 applicable rules and the
Daml-native checks.

### 5.1 The four layers

| Layer | When it runs | Is the result in the DAR? | Evidence |
|---|---|---|---|
| **damlc errors** (type checker, serializability, interface completeness, key maintainers referencing only the key, unique choice names per module, upper-case template/choice names, no party literals, out-of-range numeric literals) | `daml build` | Code that fails never produces a DAR | — |
| **damlc warnings** (GHC `-Wunused-binds`, `-Wunused-matches`, `-Wname-shadowing`, …; Daml `-Wdeprecated-exceptions`, `-Wupgrade-interfaces`, `-Wupgrade-exceptions`, `-Wtemplate-interface-depends-on-daml-script`) | `daml build` | No — warnings are not stored | Splice enables `-Wunused-binds` / `-Wunused-matches` explicitly in 33 `daml.yaml` files (so they are **not default**) and disables `-Wno-deprecated-exceptions` (5), `-Wno-upgrade-interfaces` (3), `-Wno-upgrade-exceptions` (2) |
| **dlint** (hlint-based Daml linter) | Daml IDE only | No | Splice `.dlint.yaml` header: dlint "only runs in the Daml IDE; `daml build`, `daml test` and CI never run it"; Splice sets `- ignore: {}` (all hints disabled) |
| **Upgrade validation** (damlc with `upgrades:` in `daml.yaml`; participant check on package upload/vetting) | build (if configured) / upload | No | No Splice `daml.yaml` sets `upgrades:` |
| **Engine runtime checks** (authorization, `ensure`, Int64 overflow, fetch of archived contract, empty signatories) | transaction submission | n/a | Failures abort the transaction |

Consequences:

* **damlc errors → nothing to detect.** Rules whose only purpose is to find what damlc
  rejects were moved to N/A (§4.5: uninitialised values, purity, unimplemented interface
  methods, party literals, capitalisation, mixed LF versions, name clashes).
* **Warnings and dlint → keep, but downgrade.** They are opt-in or suppressible, never
  enforced in CI by default, and invisible in the DAR. A third party auditing a DAR has no
  way to know whether they ran. These checks are emitted as **Informational** and tagged
  `compiler-overlap` so they can be disabled with one flag (`--exclude-compiler-overlap`).
* **Upgrade validation → keep at full severity.** Only runs when `upgrades:` is
  configured or at upload time; the scanner is useful *before* upload and when comparing
  arbitrary versions.
* **Runtime checks → shape the detectors, do not replace them.** The engine rejects a
  transaction lacking authority, so authorization detectors must not report "missing
  authority" (it can never succeed). They report **design flaws where authority is
  legitimately present** — controller from argument, delegation via signatory-backed
  choices, non-signatory consuming choices. Likewise `ensure` is enforced at runtime, so
  the check is about a *missing or weak* `ensure`, not a failing one.

### 5.2 Per-rule decision for overlapping checks (6 of 36)

| # | Check | Overlaps with | Visible in Daml-LF? | Decision |
|---|---|---|---|---|
| 1 | `boolean-equal` | dlint (IDE only, often disabled) | ✅ `EQUAL x True` survives | Keep, Informational |
| 2 | `boolean-cst` | dlint | ✅ partly (GHC may simplify some constants) | Keep, Informational |
| 5 | `redundant-statements` | `-Wunused-binds` (opt-in) | ⚠ only bindings damlc did not optimise away | Keep, Informational, low confidence |
| 28 | `ignored-optional` | `-Wunused-matches` (opt-in, unused *pattern* vars only) | ✅ | Keep at Medium — the compiler does not flag `fromSome` or a discarded `Optional` |
| 32 | `scu-incompatible` | damlc `upgrades:` + participant validation | ✅ (diff of two DARs) | Keep at High — runs without project config and before upload |
| 33 | `deprecated-feature` | `-Wdeprecated-exceptions` (suppressible) | ✅ `throw` / `try_catch` | Keep, Informational |

The remaining **30 applicable rules have no compiler, linter or upgrade-validation
counterpart** and are the core of the Slither-derived catalogue.

### 5.3 Daml-native checks vs compiler/runtime

| Check (§7) | Compiler | Runtime | Why the scanner is still needed |
|---|---|---|---|
| `controller-from-argument`, `unprotected-archive`, `delegated-authority-leak` | — | Authority is checked, but these patterns *have* authority | Design flaw, engine accepts it |
| `unvalidated-cid-argument`, `untrusted-interface-exercise` | — | Only type of the contract is checked | Field-level trust is the author's job |
| `asset-duplication`, `stuck-asset` | — | — | Business-logic invariant |
| `missing-ensure`, `missing-amount-check` | — | `ensure` enforced only if written | Absence is not an error |
| `over-disclosure` | — | — | Privacy policy, not correctness |
| `unsafe-coerce` | — (allowed functions) | Type re-checked on fetch in some paths | Escapes static typing |
| `hardcoded-party` | E for literals | — | Only `partyFromText`/`partyToText` comparisons remain detectable |
| `catch-all-exception`, `deprecated-feature` | W `-Wdeprecated-exceptions` | — | Warning is suppressible (Splice suppresses it) |
| `partial-function` | GHC incomplete-pattern warnings (opt-in) | Aborts at runtime | DoS on attacker-chosen input; pattern-failure helpers not found in the Splice corpus — **unverified** how they appear in LF |
| `scu-incompatible` | U if configured | Participant rejects on upload | Early detection, cross-version audit |
| `debug-trace` | — | — | Leaks data into participant logs |

---

## 6. Mythril modules → Daml

### 6.1 How Mythril checks differ from Slither checks

Slither rules are **syntactic/dataflow patterns** ("this value flows there"). Mythril modules
are **properties checked on symbolic execution paths**: LASER executes every reachable path
with symbolic inputs, modules hook opcodes, and z3 decides whether an attacker-controlled
input (over one or several transactions) can make the bad state happen. A finding comes
with a **concrete transaction sequence** that reproduces it. For Daml the equivalent output
is a runnable **Daml Script**.

Consequences:

* Most Mythril modules have a cheap **static approximation** that fits into the Slither-style
  tiers (T1/T2). The symbolic version (T3) adds a proof of reachability and an exploit, and
  so has far fewer false positives.
* Mythril's attacker model (CREATOR, ATTACKER and SOMEGUY actors, multi-transaction
  exploration) is the part with no Slither counterpart. It is also what Daml needs most:
  "can party X, acting alone, end up with Y?"

### 6.2 All 17 Mythril modules

| # | Module (file) | SWC | How Mythril detects it | Daml verdict | Daml check / example | Static approx. | Needs T3 for |
|---|---|---|---|---|---|---|---|
| 1 | EtherThief (`ether_thief.py`) | 105 | PotentialIssue at end of tx: `balance[ATTACKER] > initial` with `sender == ATTACKER` solvable | **ADAPT, most valuable** | `asset-theft`: an attacker party ends a choice sequence owning more `Holding` amount, or owning a contract it did not own, e.g. `Split` with a negative amount, or `Merge` over cids the attacker supplies | `value-to-arbitrary-party`, `unvalidated-cid-argument` (T2) | proof plus multi-tx exploit |
| 2 | AccidentallyKillable (`suicide.py`) | 106 | `SELFDESTRUCT` reachable with every caller == ATTACKER | **ADAPT** | `unauthorized-archive`: attacker can make a contract they are not a signatory of get archived (directly, or through a delegated choice of the DSO/operator) | `unprotected-archive` (T1) | indirect paths through other choices |
| 3 | Exceptions (`exceptions.py`) | 110 | `INVALID` / `Panic(0x01)` reachable on a SAT path | **PORT** | `reachable-abort`: `error`, `abort`, `assert`, `throw` or a failing `ensure` reachable with attacker-chosen args. It matters when the failing contract is **shared**, because the attacker then blocks other parties' workflows (DoS) | `partial-function` (T2) | satisfiable inputs |
| 4 | UserAssertions (`user_assertions.py`) | 110 | `AssertionFailed(string)` event or marker in `MSTORE` reachable | **PORT** | `invariant-violation`: user-declared properties (e.g. `-- @invariant sum amount preserved` or a Daml Script property) checked on every path | — | yes (core use case) |
| 5 | RequirementsViolation (`requirements_violation.py`) | 123 | `REVERT` inside a nested call (callee rejects the caller's inputs) | **ADAPT** | `nested-precondition-failure`: a choice creates or exercises with values that violate the callee template's `ensure` or assertion for some inputs | partly (T2, constant folding) | yes |
| 6 | IntegerArithmetics (`integer.py`) | 101 | taint on ADD/MUL/SUB overflow, reported only if the result reaches a sink (SSTORE, JUMPI, CALL, RETURN) | **ADAPT** | `arithmetic-abort`: Int64 overflow or `DIV_INT64` by zero, reachable from attacker input (aborts, so DoS, not wraparound); Numeric scale overflow and rounding loss in `MUL_NUMERIC`/`DIV_NUMERIC`. Keep the lazy taint-to-sink idea | `divide-before-multiply` (T2) | bound proofs |
| 7 | TransactionOrderDependence (`transaction_order_dependence.py`) | 114 | CALL value depends on BALANCE/SLOAD written by another sender | **ADAPT** | `front-running`: an observer of a consuming offer or contested contract can exercise it first. Ordering is decided by the Canton sequencer and every stakeholder sees the contract (e.g. claiming an open `TransferOffer`, racing on `OpenMiningRound`) | `contention-hotspot` (T1–T2) | multi-party ordering |
| 8 | PredictableVariables (`dependence_on_predictable_vars.py`) | 116/120 | TIMESTAMP, NUMBER, BLOCKHASH, … taint into a JUMPI condition | **ADAPT** | `time-manipulation`: `getTime` flows into a branch or an amount. The **submitter picks ledger time** within the allowed skew, so deadlines and expiry checks within the skew window are attacker-controlled | `time-dependence` (T2) | skew-window reasoning |
| 9 | ArbitraryDelegateCall (`delegatecall.py`) | 112 | `DELEGATECALL` to ATTACKER address solvable | **ADAPT** | `untrusted-interface-exercise`: exercise or fetch on an interface `ContractId` the attacker supplies, so code from the attacker's package runs with this choice's authority | same (T2) | showing what the implementation can do with that authority |
| 10 | ArbitraryStorage (`arbitrary_write.py`) | 124 | `SSTORE` to an attacker-chosen slot solvable | **ADAPT** | `confused-deputy-cid`: attacker passes a `ContractId` of **someone else's** contract where the choice's signatory (e.g. DSO/operator) is a stakeholder, so the fetch/exercise is authorised by the deputy's authority | `unvalidated-cid-argument` (T2) | yes, which contracts are reachable |
| 11 | TxOrigin (`dependence_on_origin.py`) | 115 | `ORIGIN` taint into a JUMPI condition | **ADAPT (weak)** | `identity-from-data`: authorization decision based on a `Party` taken from data (`partyFromText`, an arg field) rather than from signatories or controllers | `controller-from-argument`, `hardcoded-party` (T1) | — |
| 12 | MultipleSends (`multiple_sends.py`) | 113 | more than one CALL in one tx | **ADAPT (weak)** | `batch-all-or-nothing`: several transfers in one choice, where one failing (e.g. an archived recipient preapproval) blocks the rest | `ledger-op-in-loop` (T2) | — |
| 13 | UnexpectedEther (`unexpected_ether.py`) | 132 | strict `==` on BALANCE (ether can be force-sent) | **ADAPT (weak)** | `strict-equality-on-external-state`: `==` on counts or amounts that another party can change (e.g. the number of holdings returned by a query, or a pool total) | `incorrect-equality` (T2) | — |
| 14 | ExternalCalls (`external_calls.py`) | 107 | CALL to an attacker address with gas > 2300 | **N/A** | No reentrancy, no gas. Closest analogue is #9 | — | — |
| 15 | StateChangeAfterCall (`state_change_external_calls.py`) | 107 | SSTORE/SLOAD after an external call | **N/A** | A consuming choice archives `this` before its body runs; contracts are immutable | — | — |
| 16 | UncheckedRetval (`unchecked_retval.py`) | 104 | call return value both 0 and 1 possible at tx end | **N/A** | Daml failures abort the whole transaction; there is no return code to ignore | — | — |
| 17 | ArbitraryJump (`arbitrary_jump.py`) | 127 | symbolic JUMP target | **N/A** | Daml-LF has structured control flow (`case`/`app`), no computed jumps | — | — |

**Tally:** 2 PORT, 8 ADAPT, 3 weak ADAPT, 4 N/A. All 13 applicable modules can be
approximated statically. The symbolic tier is what turns #1, #3, #4, #5, #6, #7 and #10
from "possible" into "proven, with an exploit script".

Compiler overlap: none. Everything Mythril looks for is a **runtime** property. damlc
cannot see it, and the Daml engine only aborts the transaction; it does not prevent the
successful but unwanted outcomes in #1, #2, #7, #8, #9 and #10.

Runtime overlap: the engine aborts on overflow, failed `ensure`, missing authority and
archived-contract fetch. Mythril-style modules therefore report **reachability by an
attacker-controlled input** (a DoS or a successful unwanted outcome), never the abort
itself.

### 6.3 Engine components

Mythril's current infrastructure (LASER plugins and search strategies) and what carries
over:

| Mythril component | What it does now | Daml use |
|---|---|---|
| Mutation pruner | drops tx end-states that changed nothing | ✅ skip choice sequences that create or archive nothing |
| Dependency pruner | skips blocks that are unaffected by the previous tx's writes | ✅ skip choices that read no template the previous step wrote |
| Call depth limiter | caps nested calls | ✅ caps nested exercises |
| Bounded loops strategy | caps loop iterations | ✅ caps fold unrolling |
| Coverage plugin + strategy | prefers uncovered code | ✅ coverage per choice and branch |
| State merging, summaries | merge states, reuse per-tx summaries | ✅ per-choice symbolic summaries, cached by package hash |
| DFS/BFS/random/beam/pending search | path selection | ✅ unchanged |
| Concolic mode | replays a concrete trace and flips branches | ✅ replay Daml Script traces |
| RF tx prioritiser | ML ordering of function sequences | ⚠ optional |
| Report: text/markdown/json/jsonv2 (SWC) | issue output with test cases | ✅ with a Daml Script in place of calldata; our own ids in place of SWC |

Engine pieces, actor to VM:

| Mythril part | Portable? | Daml counterpart |
|---|---|---|
| Actors CREATOR / ATTACKER / SOMEGUY | ✅ | Parties: issuer/DSO, attacker, bystander |
| WorldState (accounts, storage) | ✅ concept | Active contract set (+ keys for LF1) + party knowledge (visibility) |
| Multi-tx exploration, open states | ✅ | Sequence of choice exercises submitted by attacker |
| PotentialIssue (check at committed tx end) | ✅ | Report only when the Daml transaction commits (no abort) |
| Mutation / dependency pruners | ✅ | Skip choices that read no template written by the previous tx |
| z3 + `get_transaction_sequence` | ✅ | Model → **generated Daml Script** reproducing the exploit |
| LASER stack VM, opcodes, gas, keccak | ❌ | Must write a **Daml-LF interpreter** (call-by-value lambda calculus + Update monad) with symbolic Int64/Numeric/Text/Party |

**Cheaper alternative to full symbolic execution:** concolic/fuzz testing by generating
Daml Script against the IDE ledger / Canton sandbox, using static analysis to pick
attacker parties and argument seeds. Static findings get confirmed with a runnable script.

---

## 7. Daml-native detectors (no Slither/Mythril counterpart)

"Data needed" refers to the analysis tiers in §8. Compiler/runtime overlap for each is in
§5.3.

| ID | Impact | Detects | Data needed |
|---|---|---|---|
| `controller-from-argument` | High | Choice controller depends on choice argument → anyone who sees the contract can exercise ("flexible controller") | T1 |
| `unprotected-archive` | High | Consuming choice controlled by a non-signatory (observer / arbitrary party) | T1 |
| `delegated-authority-leak` | High | Choice body creates/exercises with the signatories' authority where parties/amounts come from controller args (controller can make signatories sign arbitrary contracts) | T2 |
| `unvalidated-cid-argument` | High | `ContractId` from choice args is fetched/exercised and trusted without checking its fields against `this`/controller (e.g. owner, issuer, instrument) | T2 |
| `untrusted-interface-exercise` | High | Exercise/fetch on an interface `ContractId` from args → arbitrary implementation (other package) runs with combined authority | T2 |
| `asset-duplication` | High | Non-consuming choice creates a contract of the same template / same asset with the same signatories (minting/double-spend) | T2 |
| `missing-ensure` | Medium | Template with `Numeric`/`Int64` amount or time-window fields and no/trivial `precond` (`True`) | T1 |
| `over-disclosure` | Medium | Observers or choice observers derived from choice args / unrelated parties (privacy leak via divulgence) | T1–T2 |
| `self-transfer-not-excluded` | Medium | Sender and receiver not checked distinct in transfer-like choices | T2 |
| `unbounded-input-loop` | Medium | Ledger ops in folds over arg-provided lists | T2 |
| `contention-hotspot` | Low | Consuming choice on a shared singleton (config/rules contract) used by many controllers | T1–T2 |
| `catch-all-exception` | Medium | `try_catch` swallowing all exceptions (incl. arithmetic) and continuing | T2 |
| `partial-function` | Low | `fromSome`, `head`, `!!`, `error` on arg-derived values | T2 |
| `debug-trace` | Info | `TRACE` builtin left in production code | T1 |
| `hardcoded-party` | Medium | Party identity compared via `partyToText`/`partyFromText` against `Text` literals (party literals themselves are a damlc error) | T1 |
| `unsafe-coerce` | High | `COERCE_CONTRACT_ID`, `unsafe_from_interface` | T1 |
| `negative-key-lookup` (LF1/2.dev) | Low | `lookupByKey` returning `None` used as authorization/uniqueness proof | T2 |
| `scu-incompatible` | High | Two DAR versions: new non-Optional fields, removed fields/choices, changed choice arg/return types, changed signatories/key | T1 (diff) |
| `stuck-asset` | Medium | No owner-controlled consuming choice except `Archive` | T1 |

---

## 8. What can and cannot be done

### 8.1 Analysis tiers

| Tier | Technique | Effort | Precision | Checks enabled |
|---|---|---|---|---|
| **T1 structural** | Read template/choice metadata, resolve the `ValName` wrappers one level, pattern-match party expressions (`rec_proj this field` vs `rec_proj arg field`) — damlforge's `PartyRefs` already does this | Low | High | ~20 checks, authorization matrix, all PORT hygiene checks, SCU diff |
| **T2 dataflow** | Whole-DAR value index, dictionary resolution, effect IR per choice (create/exercise/fetch/get_time/throw with path conditions), party/cid/amount taint from choice args | Medium | Medium (higher-order code through dictionaries) | Remaining §7 checks, ADAPT detectors from Slither |
| **T3 symbolic** | Daml-LF interpreter over symbolic values + z3, attacker actors, multi-tx, Daml Script exploit output | High | High, but bounded | Mythril-style proofs: theft, unauthorized archive, reachable aborts |

### 8.2 Cannot be determined statically from a DAR

* **Compiler warnings and lint results** — not stored in the DAR; the scanner can only
  re-derive those whose pattern survives compilation to LF (§5.2). Shadowing and unused
  imports are erased and cannot be recovered.
* **Runtime authorization outcome.** The engine checks authority; statically we can only
  say an authority *path exists*. Real exploitability depends on which parties actually
  hold which contracts.
* **Party identity and topology.** Party ids, hosting participants, Canton topology,
  synchronizer assignment — off-ledger.
* **Active contract set.** Which contracts exist, their counts and contention under load.
* **Explicit disclosure / off-ledger workflows.** Who passes disclosed contracts to whom.
* **Ledger time skew** effects beyond "time is used in a branch".
* **Behaviour of interface implementations not in the DAR.** Splice token-standard
  interfaces are implemented by third-party packages; we can only flag the trust boundary.
* **Business intent.** Whether a non-consuming mint is a bug or a feature needs
  annotations or a policy file.
* **Interface conformance, interface method bodies, exception definitions** — until the
  dazl parser is patched (§3.3). These are fixable, not fundamental.

### 8.3 Precision risks

* Typeclass dictionaries (`struct_con`) and higher-order stdlib (`mapA`, `foldlA`, `forA`)
  hide ledger ops behind closures → need dictionary resolution + summaries for the common
  stdlib functions (pre-computed once per daml-stdlib version).
* damlc optimisations may remove or inline code (unused bindings, constant conditions), so
  PORT checks that mirror compiler warnings have low confidence.
* Large Splice packages (~8k values in one package, 51 archives per DAR) → summaries must
  be cached per package hash.
* Generated names (`$$sc_...`, `$$csignatory...`) need mapping back to source names for
  readable findings; use `location` + embedded sources.

---

## 9. Proposed architecture

```
.dar ──► lf/ (dazl + LF2 patches) ──► index (ValName→DefValue, all packages)
                                          │
                                          ▼
                       ir/ lower: templates, choices, effect trees, party exprs
                                          │
                     ┌────────────────────┼─────────────────────┐
                     ▼                    ▼                     ▼
              analyses/ callgraph   analyses/ taint      analyses/ authority
                     └────────────────────┼─────────────────────┘
                                          ▼
                  detectors/ (AbstractDetector)   printers/ (AbstractPrinter)
                                          ▼
                    output/ text · json · sarif · markdown checklist
```

Detector contract (Slither-style, adapted):

```python
class AbstractDetector:
    ARGUMENT: str
    HELP: str
    IMPACT: Impact          # HIGH, MEDIUM, LOW, INFORMATIONAL
    CONFIDENCE: Confidence  # HIGH, MEDIUM, LOW
    TIER: Tier              # STRUCTURAL, DATAFLOW, SYMBOLIC
    COMPILER_OVERLAP: Overlap | None  # WARNING, DLINT, UPGRADE — drives --exclude-compiler-overlap
    LF_VERSIONS: tuple[str, ...] | None
    WIKI_TITLE: str
    WIKI_DESCRIPTION: str
    WIKI_EXPLOIT_SCENARIO: str
    WIKI_RECOMMENDATION: str

    def _detect(self) -> list[Finding]: ...
```

Findings carry a stable fingerprint (sha256 of check + package id + qualified name +
location) for triage, SARIF `partialFingerprints`, and baseline files. Suppression via
`-- daml-scanner-disable-next-line <check>` in the embedded `.daml` source, plus a
`--baseline` file. Third-party detectors via entry-point group `daml_scanner.plugin`.

---

## 10. Project structure (mirrors damlforge)

Copy damlforge's packaging and tooling (`setup.py` with setuptools_scm, PEP 735 dependency
groups, Makefile targets, Apache header + `license-check`, black/isort/flake8/mypy at 100
cols, pytest + xdist, click CLI, loguru). Drop the Vyper/EVM leftovers (`make.cmd`,
`eth_abi`/`py-evm` test deps, `requires_evm_version`/`venom_xfail`/`hevm` markers,
`compiler/settings.py`).

```
daml-scanner/
├── pyproject.toml            # name=daml-scanner, requires-python>=3.11, deps: dazl>=8.9, click, loguru, pyyaml
├── setup.py                  # scm version → scanner/version.py, console_scripts: daml-scanner=scanner.cli.main:cli
├── setup.cfg                 # flake8
├── Makefile                  # dev-init, test, lint, mypy, black, flake8, isort, license-check, build, clean
├── quicktest.sh
├── docs/
│   ├── guide/                # detector wiki pages (one per ARGUMENT)
│   └── checks-feasibility.md
├── examples/
│   ├── vulnerable/           # small Daml projects, one per detector (daml.yaml + daml/)
│   └── dars/                 # real DARs (Splice) for regression
├── scanner/
│   ├── __init__.py  __main__.py  version.py  exceptions.py  utils.py
│   ├── lf/
│   │   ├── dar.py            # load_dar(): manifest, archives, embedded sources
│   │   ├── lf2.py            # Parser23 from damlforge + implements, exceptions, by-key, interface bodies
│   │   ├── builtins.py       # LF1/LF2 builtin + builtin-type tables
│   │   ├── index.py          # PackageIndex: ValName→DefValue, templates, interfaces, dictionaries
│   │   └── walk.py           # _Sum_name based recursive walker over Expr/Update
│   ├── ir/
│   │   ├── nodes.py          # frozen dataclasses: IRPackage, IRTemplate, IRChoice, IREffect(Create/Exercise/Fetch/GetTime/Throw), PartyRef, SourceSpan
│   │   ├── lower.py          # LF → IR (inlining of $$ wrappers, choice bodies)
│   │   └── summaries.py      # stdlib function effect summaries
│   ├── analyses/
│   │   ├── callgraph.py
│   │   ├── taint.py          # sources: choice args, this fields, ledger time; sinks: parties, cids, amounts
│   │   ├── authority.py      # who authorises each effect
│   │   └── upgrade.py        # SCU diff between two packages
│   ├── detectors/
│   │   ├── abstract_detector.py
│   │   ├── all_detectors.py
│   │   ├── authorization/    # controller-from-argument, unprotected-archive, delegated-authority-leak, annotated-controller
│   │   ├── assets/           # asset-duplication, stuck-asset, missing-amount-check, self-transfer, value-to-arbitrary-party, unbounded-preapproval
│   │   ├── contracts/        # unvalidated-cid-argument, untrusted-interface-exercise, unsafe-primitive, stale-fetch
│   │   ├── invariants/       # missing-ensure, partial-function, catch-all-exception, ignored-optional
│   │   ├── privacy/          # over-disclosure, hardcoded-party
│   │   ├── time/             # time-dependence, weak-randomness
│   │   ├── arithmetic/       # divide-before-multiply, incorrect-equality, tautology, tautological-compare, hash-concat-collision
│   │   ├── loops/            # ledger-op-in-loop, unbounded-input-loop
│   │   ├── upgrade/          # scu-incompatible, sdk-version, deprecated-feature
│   │   └── hygiene/          # unused-template-field, debug-trace, rtlo, boolean-equal, boolean-cst, redundant-statements, write-after-write, cyclomatic-complexity
│   ├── printers/
│   │   ├── abstract_printer.py
│   │   ├── all_printers.py
│   │   └── auth_matrix.py  call_graph.py  effects.py  summary.py  ir_dump.py
│   ├── output/
│   │   ├── finding.py        # Finding, fingerprint
│   │   ├── text.py  json.py  sarif.py  markdown.py
│   │   └── triage.py         # suppression comments, baseline
│   └── cli/
│       ├── main.py           # click group
│       ├── scan.py           # daml-scanner scan app.dar [--detect ..] [--exclude ..] [--exclude-compiler-overlap] [--sarif out] [--fail-on high]
│       ├── print.py          # daml-scanner print auth-matrix app.dar
│       ├── upgrade.py        # daml-scanner upgrade-check old.dar new.dar
│       └── list.py           # list-detectors / list-printers
└── tests/                    # mirrors scanner/: lf/, ir/, analyses/, detectors/, printers/, cli/
```

---

## 11. Suggested roadmap

| Phase | Deliverable | Checks |
|---|---|---|
| 0 | `lf/` loader + LF2 patches (`implements`, exceptions, builtins, by-key) + walker; regression over `damlforge/examples/dars` | — |
| 1 | IR for templates/choices + authorization matrix printer + T1 detectors + JSON/SARIF | controller-from-argument, unprotected-archive, missing-ensure, missing-amount-check, over-disclosure, unsafe-primitive, debug-trace, hardcoded-party, stuck-asset, sdk-version, unused-template-field, rtlo, tautological-compare, boolean-equal, boolean-cst |
| 2 | Value index + dictionary resolution + effect IR + taint | delegated-authority-leak, unvalidated-cid-argument, untrusted-interface-exercise, asset-duplication, value-to-arbitrary-party, time-dependence, weak-randomness, divide-before-multiply, incorrect-equality, hash-concat-collision, ledger-op-in-loop, unbounded-input-loop, stale-fetch, partial-function, ignored-optional, catch-all-exception, write-after-write |
| 3 | `upgrade-check` (SCU diff of two DARs) + dazl `implements` patch | scu-incompatible, missing-interface-instance, token-standard-conformance |
| 4 | Daml Script exploit generation (concolic) and/or LF symbolic interpreter + z3 | Mythril-style: asset theft, unauthorized archive, reachable abort |
