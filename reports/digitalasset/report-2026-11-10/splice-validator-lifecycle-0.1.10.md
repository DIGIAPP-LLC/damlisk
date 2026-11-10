# splice-validator-lifecycle-0.1.10

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-validator-lifecycle 0.1.10 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 2

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | High | `missing-ensure` | `Splice/ValidatorOnboarding.daml:24` | Splice.ValidatorOnboarding:ValidatorOnboarding: no ensure constrains `expiresAt` |
| Informational | Medium | `unused-template-field` | `Splice/ValidatorOnboarding.daml:54` | Splice.ValidatorOnboarding:UsedSecret: no code reads `secret`, `validator` |
