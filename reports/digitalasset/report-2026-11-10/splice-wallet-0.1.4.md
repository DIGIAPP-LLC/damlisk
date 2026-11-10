# splice-wallet-0.1.4

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-wallet 0.1.4 (LF 2.1)
- **SDK:** 3.0.0-snapshot.20240318.12913.0.v1c415c97
- **Findings:** 14

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferOffer.daml:50` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Accept: archived by non-signatory controller `receiver` |
| High | Medium | `unprotected-archive` | `Splice/Wallet/TransferOffer.daml:59` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Reject: archived by non-signatory controller `receiver` |
| Medium | High | `missing-ensure` | `Splice/Wallet/BuyTrafficRequest.daml:31` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest: no ensure constrains `expiresAt`, `trafficAmount`, `migrationId` |
| Medium | High | `missing-ensure` | `Splice/Wallet/TopUpState.daml:17` | Splice.Wallet.TopUpState:ValidatorTopUpState: no ensure constrains `migrationId`, `lastPurchasedAt` |
| Medium | High | `missing-ensure` | `Splice/Wallet/TransferOffer.daml:101` | Splice.Wallet.TransferOffer:AcceptedTransferOffer: no ensure constrains `expiresAt` |
| Low | Medium | `time-dependence` | `Splice/Wallet/BuyTrafficRequest.daml:60` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest.BuyTrafficRequest_Cancel: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/BuyTrafficRequest.daml:44` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest.BuyTrafficRequest_Complete: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/BuyTrafficRequest.daml:70` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest.BuyTrafficRequest_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Install.daml:317` | Splice.Wallet.Install:WalletAppInstall.WalletAppInstall_ExecuteBatch: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:112` | Splice.Wallet.TransferOffer:AcceptedTransferOffer.AcceptedTransferOffer_Complete: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:160` | Splice.Wallet.TransferOffer:AcceptedTransferOffer.AcceptedTransferOffer_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:50` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Accept: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/TransferOffer.daml:76` | Splice.Wallet.TransferOffer:TransferOffer.TransferOffer_Expire: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/BuyTrafficRequest.daml:31` | Splice.Wallet.BuyTrafficRequest:BuyTrafficRequest: no code reads `dso` |
