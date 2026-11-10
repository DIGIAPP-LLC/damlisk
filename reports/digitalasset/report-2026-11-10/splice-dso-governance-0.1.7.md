# splice-dso-governance-0.1.7

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-dso-governance 0.1.7 (LF 2.1)
- **SDK:** 3.0.0-snapshot.20240318.12913.0.v1c415c97
- **Findings:** 35

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/DsoRules.daml:559` | Splice.DsoRules:DsoRules.DsoRules_ElectDsoDelegate: controlled by unchecked argument `actor` |
| High | Medium | `delegated-authority-leak` | `Splice/DsoRules.daml:860` | Splice.DsoRules:DsoRules.DsoRules_OnboardValidator: argument `validator` used with the signatories' authority |
| High | Medium | `delegated-authority-leak` | `Splice/DsoRules.daml:884` | Splice.DsoRules:DsoRules.DsoRules_StartSvOnboarding: argument `candidateParty` used with the signatories' authority |
| High | Medium | `unprotected-archive` | `Splice/DsoRules.daml:945` | Splice.DsoRules:DsoRules.DsoRules_ExpireSvOnboardingConfirmed: archived by non-signatory controller `dsoDelegate` |
| Medium | High | `missing-ensure` | `Splice/DSO/SvState.daml:99` | Splice.DSO.SvState:SvStatusReport: no ensure constrains `number` |
| Medium | High | `missing-ensure` | `Splice/DsoBootstrap.daml:21` | Splice.DsoBootstrap:DsoBootstrap: no ensure constrains `sv1RewardWeight`, `amuletPrice` |
| Medium | High | `missing-ensure` | `Splice/DsoRules.daml:289` | Splice.DsoRules:Confirmation: no ensure constrains `expiresAt` |
| Medium | High | `missing-ensure` | `Splice/DsoRules.daml:271` | Splice.DsoRules:ElectionRequest: no ensure constrains `epoch` |
| Medium | High | `missing-ensure` | `Splice/DsoRules.daml:310` | Splice.DsoRules:VoteRequest: no ensure constrains `voteBefore` |
| Medium | High | `missing-ensure` | `Splice/SvOnboarding.daml:40` | Splice.SvOnboarding:SvOnboardingConfirmed: no ensure constrains `svRewardWeight`, `expiresAt` |
| Medium | High | `missing-ensure` | `Splice/SvOnboarding.daml:17` | Splice.SvOnboarding:SvOnboardingRequest: no ensure constrains `expiresAt` |
| Medium | Medium | `unbounded-input-loop` | `Splice/DsoRules.daml:559` | Splice.DsoRules:DsoRules.DsoRules_ElectDsoDelegate: loop over argument `requestCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/DsoRules.daml:765` | Splice.DsoRules:DsoRules.DsoRules_GarbageCollectAmuletPriceVotes: loop over argument `duplicateVoteCids`, `nonSvVoteCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/DsoRules.daml:1052` | Splice.DsoRules:DsoRules.DsoRules_ReceiveSvRewardCoupon: loop over argument `beneficiaries` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:559` | Splice.DsoRules:DsoRules.DsoRules_ElectDsoDelegate: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:614` | Splice.DsoRules:DsoRules.DsoRules_ExecuteConfirmedAction: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:765` | Splice.DsoRules:DsoRules.DsoRules_GarbageCollectAmuletPriceVotes: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:1163` | Splice.DsoRules:DsoRules.DsoRules_MergeSvRewardState: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:1052` | Splice.DsoRules:DsoRules.DsoRules_ReceiveSvRewardCoupon: create inside a loop |
| Low | Medium | `missing-amount-check` | `Splice/DsoBootstrap.daml:21` | Splice.DsoBootstrap:DsoBootstrap: ensure does not check `amuletPrice` |
| Low | Medium | `partial-function` | `Splice/DsoRules.daml:425` | Splice.DsoRules:DsoRules.DsoRules_OffboardSv: argument reaches partial function: `sv` -> head |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:298` | Splice.DsoRules:Confirmation.Confirmation_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:674` | Splice.DsoRules:DsoRules.DsoRules_CastVote: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:697` | Splice.DsoRules:DsoRules.DsoRules_CloseVoteRequest: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:1140` | Splice.DsoRules:DsoRules.DsoRules_ExpireStaleConfirmation: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:1178` | Splice.DsoRules:DsoRules.DsoRules_PruneAmuletConfigSchedule: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:1052` | Splice.DsoRules:DsoRules.DsoRules_ReceiveSvRewardCoupon: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:638` | Splice.DsoRules:DsoRules.DsoRules_RequestVote: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/SvOnboarding.daml:53` | Splice.SvOnboarding:SvOnboardingConfirmed.SvOnboardingConfirmed_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/SvOnboarding.daml:30` | Splice.SvOnboarding:SvOnboardingRequest.SvOnboardingRequest_Expire: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/DSO/SvState.daml:99` | Splice.DSO.SvState:SvStatusReport: no code reads `status` |
| Informational | Medium | `unused-template-field` | `Splice/DsoRules.daml:271` | Splice.DsoRules:ElectionRequest: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/DsoRules.daml:310` | Splice.DsoRules:VoteRequest: no code reads `requester`, `reason` |
| Informational | Medium | `unused-template-field` | `Splice/SvOnboarding.daml:40` | Splice.SvOnboarding:SvOnboardingConfirmed: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/SvOnboarding.daml:17` | Splice.SvOnboarding:SvOnboardingRequest: no code reads `candidateParticipantId`, `token`, `sponsor` |
