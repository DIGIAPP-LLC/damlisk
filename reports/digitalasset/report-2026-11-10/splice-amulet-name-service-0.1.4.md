# splice-amulet-name-service-0.1.4

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-amulet-name-service 0.1.4 (LF 2.1)
- **SDK:** 3.0.0-snapshot.20240318.12913.0.v1c415c97
- **Findings:** 3

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | High | `missing-ensure` | `Splice/Ans.daml:289` | Splice.Ans:AnsEntry: no ensure constrains `expiresAt` |
| Low | Medium | `time-dependence` | `Splice/Ans.daml:300` | Splice.Ans:AnsEntry.AnsEntry_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Ans.daml:128` | Splice.Ans:AnsRules.AnsRules_CollectEntryRenewalPayment: ledger time decides a branch |
