# splice-wallet-payments-0.1.24

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-wallet-payments 0.1.24 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 9

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Low | Medium | `missing-amount-check` | `Splice/Wallet/Subscriptions.daml:197` | Splice.Wallet.Subscriptions:SubscriptionInitialPayment: ensure does not check `targetAmount` |
| Low | Medium | `missing-amount-check` | `Splice/Wallet/Subscriptions.daml:315` | Splice.Wallet.Subscriptions:SubscriptionPayment: ensure does not check `targetAmount` |
| Low | Medium | `time-dependence` | `Splice/Wallet/Payment.daml:115` | Splice.Wallet.Payment:AppPaymentRequest.AppPaymentRequest_Accept: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Payment.daml:105` | Splice.Wallet.Payment:AppPaymentRequest.AppPaymentRequest_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Subscriptions.daml:290` | Splice.Wallet.Subscriptions:SubscriptionIdleState.SubscriptionIdleState_ExpireSubscription: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Subscriptions.daml:268` | Splice.Wallet.Subscriptions:SubscriptionIdleState.SubscriptionIdleState_MakePayment: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Wallet/Subscriptions.daml:169` | Splice.Wallet.Subscriptions:SubscriptionRequest.SubscriptionRequest_AcceptAndMakePayment: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/Payment.daml:181` | Splice.Wallet.Payment:TerminatedAppPayment: no code reads `reference` |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/Subscriptions.daml:139` | Splice.Wallet.Subscriptions:TerminatedSubscription: no code reads `reference` |
