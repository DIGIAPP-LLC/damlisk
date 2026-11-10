# splice-amulet-name-service-0.1.26

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-amulet-name-service 0.1.26 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 7

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/Ans.daml:308` | Splice.Ans:AnsEntry.AnsEntry_Expire: controlled by unchecked argument `*` |
| High | Medium | `controller-from-argument` | `Splice/Ans.daml:237` | Splice.Ans:AnsEntryContext.AnsEntryContext_Terminate: controlled by unchecked argument `*` |
| High | Medium | `unprotected-archive` | `Splice/Ans/AmuletConversionRateFeed.daml:43` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed.AmuletConversionRateFeed_ArchiveAsDso: archived by non-signatory controller `dso` |
| Medium | High | `missing-ensure` | `Splice/Ans/AmuletConversionRateFeed.daml:33` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed: no ensure constrains `amuletConversionRate` |
| Medium | High | `missing-ensure` | `Splice/Ans.daml:297` | Splice.Ans:AnsEntry: no ensure constrains `expiresAt` |
| Low | Medium | `missing-amount-check` | `Splice/Ans/AmuletConversionRateFeed.daml:33` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed: ensure does not check `amuletConversionRate` |
| Informational | Medium | `unused-template-field` | `Splice/Ans/AmuletConversionRateFeed.daml:33` | Splice.Ans.AmuletConversionRateFeed:AmuletConversionRateFeed: no code reads `amuletConversionRate` |
