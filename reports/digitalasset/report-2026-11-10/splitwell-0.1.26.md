# splitwell-0.1.26

[Back to the summary](../report-2026-11-10.md)

- **Package:** splitwell 0.1.26 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 2

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/Splitwell.daml:275` | Splice.Splitwell:TransferInProgress.TransferInProgress_Terminate: controlled by unchecked argument `*` |
| Informational | Medium | `unused-template-field` | `Splice/Splitwell.daml:315` | Splice.Splitwell:BalanceUpdate: no code reads `update` |
