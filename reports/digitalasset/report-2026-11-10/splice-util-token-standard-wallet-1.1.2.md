# splice-util-token-standard-wallet-1.1.2

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-util-token-standard-wallet 1.1.2 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 2

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Low | Medium | `ledger-op-in-loop` | `Splice/Util/Token/Wallet/BatchingUtilityV2.daml:174` | Splice.Util.Token.Wallet.BatchingUtilityV2:BatchingUtility.BatchingUtility_ExecuteBatch: exercise, fetch inside a loop |
| Informational | Medium | `unused-template-field` | `Splice/Util/Token/Wallet/MergeDelegation.daml:47` | Splice.Util.Token.Wallet.MergeDelegation:MergeDelegation: no code reads `meta` |
