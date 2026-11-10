# splice-util-featured-app-proxies-1.0.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-util-featured-app-proxies 1.0.0 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 6

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:84` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_AllocationFactory_Allocate: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:93` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_Allocation_Withdraw: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:48` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_TransferFactory_Transfer: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:57` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_TransferInstruction_Accept: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:66` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_TransferInstruction_Reject: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:75` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_TransferInstruction_Withdraw: interface contract id from argument `proxyArg` |
