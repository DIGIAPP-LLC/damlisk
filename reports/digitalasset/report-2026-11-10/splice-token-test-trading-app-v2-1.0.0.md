# splice-token-test-trading-app-v2-1.0.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-token-test-trading-app-v2 1.0.0 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 17

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `unchecked-fetch` | `Splice/Testing/Apps/TradingAppV2.daml:238` | Splice.Testing.Apps.TradingAppV2:OTCTrade.OTCTrade_Cancel: fetched contract `allocationRequestCids` is used without validation |
| High | Medium | `unchecked-fetch` | `Splice/Testing/Apps/TradingAppV2.daml:152` | Splice.Testing.Apps.TradingAppV2:OTCTrade.OTCTrade_Settle: fetched contract `allocationRequests` is used without validation |
| High | Medium | `unchecked-fetch` | `Splice/Testing/Apps/TradingAppV2.daml:348` | Splice.Testing.Apps.TradingAppV2:TradeSettlementAgreement.TradeSettlementAgreement_CancelAsSender: fetched contract `receiverAgreementCid` is used without validation |
| High | Medium | `unchecked-fetch` | `Splice/Testing/Apps/TradingAppV2.daml:325` | Splice.Testing.Apps.TradingAppV2:TradeSettlementAgreement.TradeSettlementAgreement_ExecuteTransferAsSender: fetched contract `receiverAgreementCid` is used without validation |
| High | High | `unsafe-primitive` | `Splice/Testing/Apps/TradingAppV2.daml:289` | Splice.Testing.Apps.TradingAppV2:mkOtcTradeSettlementInfoV2: unsafe primitive `coerceContractId` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Testing/Apps/TradingAppV2.daml:361` | Splice.Testing.Apps.TradingAppV2:TradeSettlementAgreement.TradeSettlementAgreement_CancelAsReceiver: interface contract id from argument `allocationCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Testing/Apps/TradingAppV2.daml:348` | Splice.Testing.Apps.TradingAppV2:TradeSettlementAgreement.TradeSettlementAgreement_CancelAsSender: interface contract id from argument `allocationCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Testing/Apps/TradingAppV2.daml:371` | Splice.Testing.Apps.TradingAppV2:TradeSettlementAgreement.TradeSettlementAgreement_CreateReceiptAllocation: interface contract id from argument `factoryCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Testing/Apps/TradingAppV2.daml:338` | Splice.Testing.Apps.TradingAppV2:TradeSettlementAgreement.TradeSettlementAgreement_ExecuteTransferAsReceiver: interface contract id from argument `allocationCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Testing/Apps/TradingAppV2.daml:325` | Splice.Testing.Apps.TradingAppV2:TradeSettlementAgreement.TradeSettlementAgreement_ExecuteTransferAsSender: interface contract id from argument `allocationCid` |
| Medium | High | `missing-ensure` | `Splice/Testing/Apps/TradingAppV2.daml:119` | Splice.Testing.Apps.TradingAppV2:OTCTrade: no ensure constrains `createdAt`, `settleAt` |
| Medium | High | `missing-ensure` | `Splice/Testing/Apps/TradingAppV2.daml:31` | Splice.Testing.Apps.TradingAppV2:OTCTradeAllocationRequest: no ensure constrains `requestedAt`, `settleAt` |
| Medium | Medium | `unbounded-input-loop` | `Splice/Testing/Apps/TradingAppV2.daml:238` | Splice.Testing.Apps.TradingAppV2:OTCTrade.OTCTrade_Cancel: loop over argument `allocationRequestCids`, `allocationsWithContextV1`, `allocationsWithContextV2` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/Testing/Apps/TradingAppV2.daml:152` | Splice.Testing.Apps.TradingAppV2:OTCTrade.OTCTrade_Settle: loop over argument `allocationRequests` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/Testing/Apps/TradingAppV2.daml:238` | Splice.Testing.Apps.TradingAppV2:OTCTrade.OTCTrade_Cancel: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/Testing/Apps/TradingAppV2.daml:128` | Splice.Testing.Apps.TradingAppV2:OTCTrade.OTCTrade_RequestAllocations: create inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/Testing/Apps/TradingAppV2.daml:152` | Splice.Testing.Apps.TradingAppV2:OTCTrade.OTCTrade_Settle: exercise, fetch inside a loop |
