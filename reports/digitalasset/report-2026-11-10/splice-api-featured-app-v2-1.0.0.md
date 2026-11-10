# splice-api-featured-app-v2-1.0.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-api-featured-app-v2 1.0.0 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 1

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | Medium | `over-disclosure` | `Splice/Api/FeaturedAppRightV2.daml:22` | Splice.Api.FeaturedAppRightV2:FeaturedAppRight.FeaturedAppRight_CreateActivityMarker: choice observers taken from argument `beneficiaries` |
