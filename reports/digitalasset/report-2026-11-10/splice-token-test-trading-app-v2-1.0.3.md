# splice-token-test-trading-app-v2-1.0.3

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-token-test-trading-app-v2 1.0.3 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 3

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | High | `unsafe-primitive` | `Splice/Testing/Apps/TradingAppV2.daml:288` | Splice.Testing.Apps.TradingAppV2:mkOtcTradeSettlementInfoV2: unsafe primitive `coerceContractId` |
| Medium | High | `missing-ensure` | `Splice/Testing/Apps/TradingAppV2.daml:119` | Splice.Testing.Apps.TradingAppV2:OTCTrade: no ensure constrains `createdAt`, `settleAt` |
| Medium | High | `missing-ensure` | `Splice/Testing/Apps/TradingAppV2.daml:31` | Splice.Testing.Apps.TradingAppV2:OTCTradeAllocationRequest: no ensure constrains `requestedAt`, `settleAt` |
