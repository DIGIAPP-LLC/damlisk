# splice-token-test-trading-app-1.0.4

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-token-test-trading-app 1.0.4 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 5

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/Testing/Apps/TradingApp.daml:31` | Splice.Testing.Apps.TradingApp:OTCTradeProposal.OTCTradeProposal_Accept: controlled by unchecked argument `*` |
| High | Medium | `controller-from-argument` | `Splice/Testing/Apps/TradingApp.daml:44` | Splice.Testing.Apps.TradingApp:OTCTradeProposal.OTCTradeProposal_Reject: controlled by unchecked argument `*` |
| High | Medium | `unprotected-archive` | `Splice/Testing/Apps/TradingApp.daml:50` | Splice.Testing.Apps.TradingApp:OTCTradeProposal.OTCTradeProposal_InitiateSettlement: archived by non-signatory controller `venue` |
| High | High | `unsafe-primitive` | `Splice/Testing/Apps/TradingApp.daml:184` | Splice.Testing.Apps.TradingApp:makeTradeRef: unsafe primitive `coerceContractId` |
| Medium | High | `missing-ensure` | `Splice/Testing/Apps/TradingApp.daml:80` | Splice.Testing.Apps.TradingApp:OTCTrade: no ensure constrains `createdAt`, `prepareUntil`, `settleBefore` |
