# splice-wallet-0.1.26

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-wallet 0.1.26 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 10

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/Wallet/TransferOffer.daml:179` | Splice.Wallet.TransferOffer:AcceptedTransferOffer.AcceptedTransferOffer_Expire: controlled by unchecked argument `*` |
| High | Medium | `controller-from-argument` | `Splice/Wallet/TransferOffer.daml:92` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Expire: controlled by unchecked argument `*` |
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferOffer.daml:66` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Accept: archived by non-signatory controller `receiver` |
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferOffer.daml:75` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Reject: archived by non-signatory controller `receiver` |
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferPreapproval.daml:20` | Splice.Wallet.TransferPreapproval:TransferPreapprovalProposal.TransferPreapprovalProposal_Accept: archived by non-signatory controller `provider` |
| Medium | High | `missing-ensure` | `Splice/Wallet/BuyTrafficRequest.daml:34` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest: no ensure constrains `expiresAt`, `trafficAmount`, `migrationId` |
| Medium | High | `missing-ensure` | `Splice/Wallet/MintingDelegation.daml:45` | Splice.Wallet.MintingDelegation:MintingDelegation: no ensure constrains `expiresAt`, `amuletMergeLimit` |
| Medium | High | `missing-ensure` | `Splice/Wallet/TopUpState.daml:17` | Splice.Wallet.TopUpState:ValidatorTopUpState: no ensure constrains `migrationId`, `lastPurchasedAt` |
| Medium | High | `missing-ensure` | `Splice/Wallet/TransferOffer.daml:118` | Splice.Wallet.TransferOffer:AcceptedTransferOffer: no ensure constrains `expiresAt` |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/MintingDelegation.daml:45` | Splice.Wallet.MintingDelegation:MintingDelegation: no code reads `amuletMergeLimit` |
