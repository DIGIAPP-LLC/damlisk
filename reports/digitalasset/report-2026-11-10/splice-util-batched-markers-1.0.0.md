# splice-util-batched-markers-1.0.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-util-batched-markers 1.0.0 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 3

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | Medium | `over-disclosure` | `Splice/Util/FeaturedApp/BatchedMarkersProxy.daml:26` | Splice.Util.FeaturedApp.BatchedMarkersProxy:BatchedMarkersProxy.BatchedMarkersProxy_CreateMarkers: choice observers taken from argument `batches` |
| Medium | Medium | `unbounded-input-loop` | `Splice/Util/FeaturedApp/BatchedMarkersProxy.daml:26` | Splice.Util.FeaturedApp.BatchedMarkersProxy:BatchedMarkersProxy.BatchedMarkersProxy_CreateMarkers: loop over argument `batches` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/Util/FeaturedApp/BatchedMarkersProxy.daml:26` | Splice.Util.FeaturedApp.BatchedMarkersProxy:BatchedMarkersProxy.BatchedMarkersProxy_CreateMarkers: exercise inside a loop |
