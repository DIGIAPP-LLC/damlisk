# splice-api-token-transfer-events-v2-1.0.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-api-token-transfer-events-v2 1.0.0 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 1

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | Medium | `over-disclosure` | `Splice/Api/Token/TransferEventsV2.daml:54` | Splice.Api.Token.TransferEventsV2:EventLog.EventLog_HoldingsChange: choice observers taken from argument `observers` |
