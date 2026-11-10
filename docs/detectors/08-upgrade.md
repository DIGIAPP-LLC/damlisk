# Upgrade detectors

Package targets and upgrade concerns.

| Detector | Impact | Confidence | What it finds |
|---|---|---|---|
| [`sdk-version`](#sdk-version) | Informational | High | DAR built for a Daml-LF 1.x target |

## sdk-version

**Daml-LF 1.x target.** It reports a DAR whose main package was compiled for Daml-LF 1.x, i.e.
with a Daml 2.x SDK.

**Impact:** Canton 3 and Splice run Daml-LF 2.x packages only, and LF 1.x packages lack smart
contract upgrades, so a fix cannot be rolled out as an upgrade of the deployed package.

**Example:** a DAR built with SDK 2.9 and `--target=1.15`:

```
$ damlisk scan old-token.dar --detect sdk-version
[Informational] sdk-version old-token
    old-token: built for Daml-LF 1.15 (SDK 2.9.4)
1 finding(s).
```

**How it works:** the detector reads the LF version of the main package from its archive
payload and the SDK from the manifest `Sdk-Version`. There is no example project: the SDKs
installed for this repository are 3.x and only build LF 2.x; the tests give a Splice DAR an
LF 1.x main package instead.

**Results on real code:** all Splice DARs target Daml-LF 2.1 (SDK 3.3 to 3.5) and have no
findings.

**Recommendation:** rebuild the package with a Daml 3.x SDK for a Daml-LF 2.x target.
