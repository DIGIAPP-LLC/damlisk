# splitwell-0.1.24

[Back to the summary](../report-2026-11-10.md)

- **Package:** splitwell 0.1.24 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 3

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `delegated-authority-leak` | `Splice/Splitwell.daml:210` | Splice.Splitwell:Group.Group_EnterPayment: argument `amount` used with the signatories' authority |
| Low | Medium | `ledger-op-in-loop` | `Splice/Splitwell.daml:285` | Splice.Splitwell:TransferInProgress.TransferInProgress_CompleteTransfer: create inside a loop |
| Informational | Medium | `unused-template-field` | `Splice/Splitwell.daml:315` | Splice.Splitwell:BalanceUpdate: no code reads `update` |
