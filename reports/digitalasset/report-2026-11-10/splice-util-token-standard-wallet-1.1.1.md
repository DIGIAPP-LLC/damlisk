# splice-util-token-standard-wallet-1.1.1

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-util-token-standard-wallet 1.1.1 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 5

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/Token/Wallet/MergeDelegation.daml:58` | Splice.Util.Token.Wallet.MergeDelegation:MergeDelegation.MergeDelegation_Merge: interface contract id from argument `optExtraTransfer`, `optFeaturedAppRight`, `optMergeTransfer` |
| Medium | Medium | `unbounded-input-loop` | `Splice/Util/Token/Wallet/BatchingUtilityV2.daml:174` | Splice.Util.Token.Wallet.BatchingUtilityV2:BatchingUtility.BatchingUtility_ExecuteBatch: loop over argument `actions` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/Util/Token/Wallet/BatchingUtilityV2.daml:174` | Splice.Util.Token.Wallet.BatchingUtilityV2:BatchingUtility.BatchingUtility_ExecuteBatch: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/Util/Token/Wallet/MergeDelegation.daml:58` | Splice.Util.Token.Wallet.MergeDelegation:MergeDelegation.MergeDelegation_Merge: exercise, fetch inside a loop |
| Informational | Medium | `unused-template-field` | `Splice/Util/Token/Wallet/MergeDelegation.daml:47` | Splice.Util.Token.Wallet.MergeDelegation:MergeDelegation: no code reads `meta` |
