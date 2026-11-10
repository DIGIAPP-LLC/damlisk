# splice-token-test-trading-app-1.0.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-token-test-trading-app 1.0.0 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 7

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/Testing/Apps/TradingApp.daml:44` | Splice.Testing.Apps.TradingApp:OTCTradeProposal.OTCTradeProposal_Reject: controlled by unchecked argument `trader` |
| High | Medium | `unprotected-archive` | `Splice/Testing/Apps/TradingApp.daml:50` | Splice.Testing.Apps.TradingApp:OTCTradeProposal.OTCTradeProposal_InitiateSettlement: archived by non-signatory controller `venue` |
| High | High | `unsafe-primitive` | `Splice/Testing/Apps/TradingApp.daml:186` | Splice.Testing.Apps.TradingApp:makeTradeRef: unsafe primitive `coerceContractId` |
| Medium | High | `missing-ensure` | `Splice/Testing/Apps/TradingApp.daml:80` | Splice.Testing.Apps.TradingApp:OTCTrade: no ensure constrains `createdAt`, `prepareUntil`, `settleBefore` |
| Low | Medium | `ledger-op-in-loop` | `Splice/Testing/Apps/TradingApp.daml:124` | Splice.Testing.Apps.TradingApp:OTCTrade.OTCTrade_Cancel: exercise, fetch inside a loop |
| Low | Medium | `time-dependence` | `Splice/Testing/Apps/TradingApp.daml:91` | Splice.Testing.Apps.TradingApp:OTCTrade.OTCTrade_Settle: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Testing/Apps/TradingApp.daml:50` | Splice.Testing.Apps.TradingApp:OTCTradeProposal.OTCTradeProposal_InitiateSettlement: ledger time decides a branch |
