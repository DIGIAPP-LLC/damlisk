# splice-validator-lifecycle-0.1.3

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-validator-lifecycle 0.1.3 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 3

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | High | `missing-ensure` | `Splice/ValidatorOnboarding.daml:20` | Splice.ValidatorOnboarding:ValidatorOnboarding: no ensure constrains `expiresAt` |
| Low | Medium | `time-dependence` | `Splice/ValidatorOnboarding.daml:41` | Splice.ValidatorOnboarding:ValidatorOnboarding.ValidatorOnboarding_Expire: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/ValidatorOnboarding.daml:50` | Splice.ValidatorOnboarding:UsedSecret: no code reads `secret`, `validator` |
