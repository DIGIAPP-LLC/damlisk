# splice-wallet-0.1.24

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-wallet 0.1.24 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 35

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferOffer.daml:66` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Accept: archived by non-signatory controller `receiver` |
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferOffer.daml:75` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Reject: archived by non-signatory controller `receiver` |
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferPreapproval.daml:20` | Splice.Wallet.TransferPreapproval:TransferPreapprovalProposal.TransferPreapprovalProposal_Accept: archived by non-signatory controller `provider` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:701` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_AllocationFactoryV2_Allocate: interface contract id from argument `allocationFactory`, `allocationReqCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:644` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_AllocationFactory_Allocate: interface contract id from argument `allocationFactory` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:736` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_AllocationInstructionV2_Accept: interface contract id from argument `allocationInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:747` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_AllocationInstructionV2_Withdraw: interface contract id from argument `allocationInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:725` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_AllocationV2_Withdraw: interface contract id from argument `allocationCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:656` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_Allocation_Withdraw: interface contract id from argument `allocationCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:669` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferFactoryV2_Transfer: interface contract id from argument `transferFactoryCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:597` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferFactory_Transfer: interface contract id from argument `transferFactoryCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:677` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferInstructionV2_Accept: interface contract id from argument `transferInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:685` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferInstructionV2_Reject: interface contract id from argument `transferInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:693` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferInstructionV2_Withdraw: interface contract id from argument `transferInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:608` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferInstruction_Accept: interface contract id from argument `transferInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:618` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferInstruction_Reject: interface contract id from argument `transferInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/Install.daml:628` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_TransferInstruction_Withdraw: interface contract id from argument `transferInstructionCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Wallet/MintingDelegation.daml:81` | Splice.Wallet.MintingDelegation:MintingDelegation.MintingDelegation_AssignAndMint: interface contract id from argument `couponCid` |
| Medium | High | `missing-ensure` | `Splice/Wallet/BuyTrafficRequest.daml:34` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest: no ensure constrains `expiresAt`, `trafficAmount`, `migrationId` |
| Medium | High | `missing-ensure` | `Splice/Wallet/MintingDelegation.daml:45` | Splice.Wallet.MintingDelegation:MintingDelegation: no ensure constrains `expiresAt`, `amuletMergeLimit` |
| Medium | High | `missing-ensure` | `Splice/Wallet/TopUpState.daml:17` | Splice.Wallet.TopUpState:ValidatorTopUpState: no ensure constrains `migrationId`, `lastPurchasedAt` |
| Medium | High | `missing-ensure` | `Splice/Wallet/TransferOffer.daml:118` | Splice.Wallet.TransferOffer:AcceptedTransferOffer: no ensure constrains `expiresAt` |
| Low | Medium | `ledger-op-in-loop` | `Splice/Wallet/Install.daml:701` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_AllocationFactoryV2_Allocate: exercise, fetch inside a loop |
| Low | Medium | `time-dependence` | `Splice/Wallet/BuyTrafficRequest.daml:71` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest.BuyTrafficRequest_Cancel: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/BuyTrafficRequest.daml:47` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest.BuyTrafficRequest_Complete: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/BuyTrafficRequest.daml:81` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest.BuyTrafficRequest_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Install.daml:421` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_ExecuteBatch: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/MintingDelegation.daml:81` | Splice.Wallet.MintingDelegation:MintingDelegation.MintingDelegation_AssignAndMint: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/MintingDelegation.daml:62` | Splice.Wallet.MintingDelegation:MintingDelegation.MintingDelegation_Mint: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:129` | Splice.Wallet.TransferOffer:AcceptedTransferOffer.AcceptedTransferOffer_Complete: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:179` | Splice.Wallet.TransferOffer:AcceptedTransferOffer.AcceptedTransferOffer_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:66` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Accept: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:92` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferPreapproval.daml:20` | Splice.Wallet.TransferPreapproval:TransferPreapprovalProposal.TransferPreapprovalProposal_Accept: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/MintingDelegation.daml:45` | Splice.Wallet.MintingDelegation:MintingDelegation: no code reads `amuletMergeLimit` |
