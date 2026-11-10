# splice-wallet-payments-0.1.25

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-wallet-payments 0.1.25 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 8

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/Wallet/Payment.daml:105` | Splice.Wallet.Payment:AppPaymentRequest.AppPaymentRequest_Expire: controlled by unchecked argument `*` |
| High | Medium | `controller-from-argument` | `Splice/Wallet/Subscriptions.daml:290` | Splice.Wallet.Subscriptions:SubscriptionIdleState.SubscriptionIdleState_ExpireSubscription: controlled by unchecked argument `*` |
| High | Medium | `controller-from-argument` | `Splice/Wallet/Subscriptions.daml:239` | Splice.Wallet.Subscriptions:SubscriptionInitialPayment.SubscriptionInitialPayment_Expire: controlled by unchecked argument `*` |
| High | Medium | `controller-from-argument` | `Splice/Wallet/Subscriptions.daml:360` | Splice.Wallet.Subscriptions:SubscriptionPayment.SubscriptionPayment_Expire: controlled by unchecked argument `*` |
| Low | Medium | `missing-amount-check` | `Splice/Wallet/Subscriptions.daml:197` | Splice.Wallet.Subscriptions:SubscriptionInitialPayment: ensure does not check `targetAmount` |
| Low | Medium | `missing-amount-check` | `Splice/Wallet/Subscriptions.daml:315` | Splice.Wallet.Subscriptions:SubscriptionPayment: ensure does not check `targetAmount` |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/Payment.daml:181` | Splice.Wallet.Payment:TerminatedAppPayment: no code reads `reference` |
| Informational | Medium | `unused-template-field` | `Splice/Wallet/Subscriptions.daml:139` | Splice.Wallet.Subscriptions:TerminatedSubscription: no code reads `reference` |
