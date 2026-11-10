# splice-util-featured-app-proxies-1.2.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-util-featured-app-proxies 1.2.0 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 12

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:81` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_AllocationFactory_Allocate: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:90` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_Allocation_Withdraw: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:45` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_TransferFactory_Transfer: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:54` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_TransferInstruction_Accept: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:63` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_TransferInstruction_Reject: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/DelegateProxy.daml:72` | Splice.Util.FeaturedApp.DelegateProxy:DelegateProxy.DelegateProxy_TransferInstruction_Withdraw: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/WalletUserProxy.daml:119` | Splice.Util.FeaturedApp.WalletUserProxy:WalletUserProxy.WalletUserProxy_AllocationFactory_Allocate: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/WalletUserProxy.daml:129` | Splice.Util.FeaturedApp.WalletUserProxy:WalletUserProxy.WalletUserProxy_Allocation_Withdraw: interface contract id from argument `cid`, `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/WalletUserProxy.daml:76` | Splice.Util.FeaturedApp.WalletUserProxy:WalletUserProxy.WalletUserProxy_TransferFactory_Transfer: interface contract id from argument `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/WalletUserProxy.daml:86` | Splice.Util.FeaturedApp.WalletUserProxy:WalletUserProxy.WalletUserProxy_TransferInstruction_Accept: interface contract id from argument `cid`, `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/WalletUserProxy.daml:97` | Splice.Util.FeaturedApp.WalletUserProxy:WalletUserProxy.WalletUserProxy_TransferInstruction_Reject: interface contract id from argument `cid`, `proxyArg` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Util/FeaturedApp/WalletUserProxy.daml:108` | Splice.Util.FeaturedApp.WalletUserProxy:WalletUserProxy.WalletUserProxy_TransferInstruction_Withdraw: interface contract id from argument `cid`, `proxyArg` |
