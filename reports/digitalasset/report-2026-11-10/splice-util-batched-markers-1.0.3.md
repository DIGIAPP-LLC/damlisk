# splice-util-batched-markers-1.0.3

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-util-batched-markers 1.0.3 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 6

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | Medium | `over-disclosure` | `Splice/Util/FeaturedApp/BatchedMarkersProxy.daml:38` | Splice.Util.FeaturedApp.BatchedMarkersProxy:BatchedMarkersProxy.BatchedMarkersProxy_CreateMarkers: choice observers taken from argument `batches` |
| Medium | Medium | `over-disclosure` | `Splice/Util/FeaturedApp/BatchedMarkersProxy.daml:53` | Splice.Util.FeaturedApp.BatchedMarkersProxy:BatchedMarkersProxy.BatchedMarkersProxy_CreateMarkersV2: choice observers taken from argument `batches` |
| Medium | Medium | `unbounded-input-loop` | `Splice/Util/FeaturedApp/BatchedMarkersProxy.daml:38` | Splice.Util.FeaturedApp.BatchedMarkersProxy:BatchedMarkersProxy.BatchedMarkersProxy_CreateMarkers: loop over argument `batches` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/Util/FeaturedApp/BatchedMarkersProxy.daml:53` | Splice.Util.FeaturedApp.BatchedMarkersProxy:BatchedMarkersProxy.BatchedMarkersProxy_CreateMarkersV2: loop over argument `batches` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/Util/FeaturedApp/BatchedMarkersProxy.daml:38` | Splice.Util.FeaturedApp.BatchedMarkersProxy:BatchedMarkersProxy.BatchedMarkersProxy_CreateMarkers: exercise inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/Util/FeaturedApp/BatchedMarkersProxy.daml:53` | Splice.Util.FeaturedApp.BatchedMarkersProxy:BatchedMarkersProxy.BatchedMarkersProxy_CreateMarkersV2: exercise inside a loop |
