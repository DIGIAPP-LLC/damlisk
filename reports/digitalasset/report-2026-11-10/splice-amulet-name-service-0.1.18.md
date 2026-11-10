# splice-amulet-name-service-0.1.18

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-amulet-name-service 0.1.18 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 9

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `unprotected-archive` | `Splice/Ans/AmuletConversionRateFeed.daml:41` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed.AmuletConversionRateFeed_ArchiveAsDso: archived by non-signatory controller `dso` |
| Medium | High | `missing-ensure` | `Splice/Ans/AmuletConversionRateFeed.daml:31` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed: no ensure constrains `amuletConversionRate` |
| Medium | High | `missing-ensure` | `Splice/Ans.daml:289` | Splice.Ans:AnsEntry: no ensure constrains `expiresAt` |
| Low | Medium | `ledger-op-in-loop` | `Splice/Ans/AmuletConversionRateFeed.daml:47` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed.AmuletConversionRateFeed_Update: exercise, fetch inside a loop |
| Low | Medium | `missing-amount-check` | `Splice/Ans/AmuletConversionRateFeed.daml:31` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed: ensure does not check `amuletConversionRate` |
| Low | Medium | `time-dependence` | `Splice/Ans/AmuletConversionRateFeed.daml:47` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed.AmuletConversionRateFeed_Update: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Ans.daml:300` | Splice.Ans:AnsEntry.AnsEntry_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Ans.daml:128` | Splice.Ans:AnsRules.AnsRules_CollectEntryRenewalPayment: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/Ans/AmuletConversionRateFeed.daml:31` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed: no code reads `amuletConversionRate` |
