# splice-util-token-standard-wallet-1.0.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-util-token-standard-wallet 1.0.0 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 3

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/Token/Wallet/MergeDelegation.daml:58` | Splice.Util.Token.Wallet.MergeDelegation:MergeDelegation.MergeDelegation_Merge: interface contract id from argument `optExtraTransfer`, `optFeaturedAppRight`, `optMergeTransfer` |
| Low | Medium | `ledger-op-in-loop` | `Splice/Util/Token/Wallet/MergeDelegation.daml:58` | Splice.Util.Token.Wallet.MergeDelegation:MergeDelegation.MergeDelegation_Merge: exercise, fetch inside a loop |
| Informational | Medium | `unused-template-field` | `Splice/Util/Token/Wallet/MergeDelegation.daml:47` | Splice.Util.Token.Wallet.MergeDelegation:MergeDelegation: no code reads `meta` |
