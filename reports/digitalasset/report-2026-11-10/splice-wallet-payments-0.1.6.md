# splice-wallet-payments-0.1.6

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-wallet-payments 0.1.6 (LF 2.1)
- **SDK:** 3.0.0-snapshot.20240318.12913.0.v1c415c97
- **Findings:** 11

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Low | Medium | `missing-amount-check` | `Splice/Wallet/Subscriptions.daml:181` | Splice.Wallet.Subscriptions:SubscriptionInitialPayment: ensure does not check `targetAmount` |
| Low | Medium | `missing-amount-check` | `Splice/Wallet/Subscriptions.daml:296` | Splice.Wallet.Subscriptions:SubscriptionPayment: ensure does not check `targetAmount` |
| Low | Medium | `time-dependence` | `Splice/Wallet/Payment.daml:106` | Splice.Wallet.Payment:AppPaymentRequest.AppPaymentRequest_Accept: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Payment.daml:96` | Splice.Wallet.Payment:AppPaymentRequest.AppPaymentRequest_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Subscriptions.daml:271` | Splice.Wallet.Subscriptions:SubscriptionIdleState.SubscriptionIdleState_ExpireSubscription: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Subscriptions.daml:249` | Splice.Wallet.Subscriptions:SubscriptionIdleState.SubscriptionIdleState_MakePayment: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Subscriptions.daml:153` | Splice.Wallet.Subscriptions:SubscriptionRequest.SubscriptionRequest_AcceptAndMakePayment: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/Payment.daml:197` | Splice.Wallet.Payment:AcceptedAppPayment: no code reads `dso` |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/Payment.daml:83` | Splice.Wallet.Payment:AppPaymentRequest: no code reads `description` |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/Payment.daml:171` | Splice.Wallet.Payment:TerminatedAppPayment: no code reads `reference` |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/Subscriptions.daml:123` | Splice.Wallet.Subscriptions:TerminatedSubscription: no code reads `reference` |
