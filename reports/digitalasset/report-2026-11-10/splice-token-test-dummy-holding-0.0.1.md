# splice-token-test-dummy-holding-0.0.1

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-token-test-dummy-holding 0.0.1 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 3

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | High | `missing-ensure` | `Splice/Api/Token/Test/DummyHolding.daml:10` | Splice.Api.Token.Test.DummyHolding:DummyHolding: no ensure constrains `amount` |
| Medium | Medium | `stuck-asset` | `Splice/Api/Token/Test/DummyHolding.daml:10` | Splice.Api.Token.Test.DummyHolding:DummyHolding: `owner` controls no consuming choice except Archive |
| Low | Medium | `missing-amount-check` | `Splice/Api/Token/Test/DummyHolding.daml:10` | Splice.Api.Token.Test.DummyHolding:DummyHolding: ensure does not check `amount` |
