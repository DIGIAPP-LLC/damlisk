# splice-app-manager-0.1.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-app-manager 0.1.0 (LF 2.1)
- **SDK:** 3.0.0-snapshot.20240318.12913.0.v1c415c97
- **Findings:** 7

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | High | `missing-ensure` | `Splice/AppManager/Store.daml:12` | Splice.AppManager.Store:AppConfiguration: no ensure constrains `version` |
| Medium | High | `missing-ensure` | `Splice/AppManager/Store.daml:60` | Splice.AppManager.Store:ApprovedReleaseConfiguration: no ensure constrains `configurationVersion` |
| Informational | Medium | `unused-template-field` | `Splice/AppManager/Store.daml:12` | Splice.AppManager.Store:AppConfiguration: no code reads `provider`, `version`, `json` |
| Informational | Medium | `unused-template-field` | `Splice/AppManager/Store.daml:28` | Splice.AppManager.Store:AppRelease: no code reads `provider`, `version`, `json` |
| Informational | Medium | `unused-template-field` | `Splice/AppManager/Store.daml:60` | Splice.AppManager.Store:ApprovedReleaseConfiguration: no code reads `provider`, `configurationVersion`, `json`, `jsonHash` |
| Informational | Medium | `unused-template-field` | `Splice/AppManager/Store.daml:50` | Splice.AppManager.Store:InstalledApp: no code reads `provider`, `appUrl` |
| Informational | Medium | `unused-template-field` | `Splice/AppManager/Store.daml:39` | Splice.AppManager.Store:RegisteredApp: no code reads `provider` |
