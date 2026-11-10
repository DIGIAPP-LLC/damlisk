# splice-validator-lifecycle-0.1.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-validator-lifecycle 0.1.0 (LF 2.1)
- **SDK:** 3.0.0-snapshot.20240318.12913.0.v1c415c97
- **Findings:** 3

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | High | `missing-ensure` | `Splice/ValidatorOnboarding.daml:17` | Splice.ValidatorOnboarding:ValidatorOnboarding: no ensure constrains `expiresAt` |
| Low | Medium | `time-dependence` | `Splice/ValidatorOnboarding.daml:38` | Splice.ValidatorOnboarding:ValidatorOnboarding.ValidatorOnboarding_Expire: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/ValidatorOnboarding.daml:47` | Splice.ValidatorOnboarding:UsedSecret: no code reads `secret`, `validator` |
