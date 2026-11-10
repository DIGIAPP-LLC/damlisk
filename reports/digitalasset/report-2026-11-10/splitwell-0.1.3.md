# splitwell-0.1.3

[Back to the summary](../report-2026-11-10.md)

- **Package:** splitwell 0.1.3 (LF 2.1)
- **SDK:** 3.0.0-snapshot.20240318.12913.0.v1c415c97
- **Findings:** 3

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `delegated-authority-leak` | `Splice/Splitwell.daml:206` | Splice.Splitwell:Group.Group_EnterPayment: argument `amount` used with the signatories' authority |
| Low | Medium | `ledger-op-in-loop` | `Splice/Splitwell.daml:281` | Splice.Splitwell:TransferInProgress.TransferInProgress_CompleteTransfer: create inside a loop |
| Informational | Medium | `unused-template-field` | `Splice/Splitwell.daml:311` | Splice.Splitwell:BalanceUpdate: no code reads `update` |
