# splice-wallet-0.1.10

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-wallet 0.1.10 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 22

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferOffer.daml:55` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Accept: archived by non-signatory controller `receiver` |
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferOffer.daml:64` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Reject: archived by non-signatory controller `receiver` |
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferPreapproval.daml:17` | Splice.Wallet.TransferPreapproval:TransferPreapprovalProposal.TransferPreapprovalProposal_Accept: archived by non-signatory controller `provider` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:624` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_AllocationFactory_Allocate: interface contract id from argument `allocationFactory` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:636` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_Allocation_Withdraw: interface contract id from argument `allocationCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:580` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferFactory_Transfer: interface contract id from argument `transferFactoryCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:591` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferInstruction_Accept: interface contract id from argument `transferInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:601` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferInstruction_Reject: interface contract id from argument `transferInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:611` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferInstruction_Withdraw: interface contract id from argument `transferInstructionCid` |
| Medium | High | `missing-ensure` | `Splice/Wallet/BuyTrafficRequest.daml:31` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest: no ensure constrains `expiresAt`, `trafficAmount`, `migrationId` |
| Medium | High | `missing-ensure` | `Splice/Wallet/TopUpState.daml:17` | Splice.Wallet.TopUpState:ValidatorTopUpState: no ensure constrains `migrationId`, `lastPurchasedAt` |
| Medium | High | `missing-ensure` | `Splice/Wallet/TransferOffer.daml:106` | Splice.Wallet.TransferOffer:AcceptedTransferOffer: no ensure constrains `expiresAt` |
| Low | Medium | `time-dependence` | `Splice/Wallet/BuyTrafficRequest.daml:60` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest.BuyTrafficRequest_Cancel: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/BuyTrafficRequest.daml:44` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest.BuyTrafficRequest_Complete: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/BuyTrafficRequest.daml:70` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest.BuyTrafficRequest_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Install.daml:406` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_ExecuteBatch: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:117` | Splice.Wallet.TransferOffer:AcceptedTransferOffer.AcceptedTransferOffer_Complete: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:166` | Splice.Wallet.TransferOffer:AcceptedTransferOffer.AcceptedTransferOffer_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:55` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Accept: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:81` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferPreapproval.daml:17` | Splice.Wallet.TransferPreapproval:TransferPreapprovalProposal.TransferPreapprovalProposal_Accept: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/BuyTrafficRequest.daml:31` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest: no code reads `dso` |
