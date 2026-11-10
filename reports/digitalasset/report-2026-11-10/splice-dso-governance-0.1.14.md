# splice-dso-governance-0.1.14

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-dso-governance 0.1.14 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 38

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/DsoRules.daml:617` | Splice.DsoRules:DsoRules.DsoRules_ElectDsoDelegate: controlled by unchecked argument `actor` |
| High | Medium | `controller-from-argument` | `Splice/DsoRules.daml:1102` | Splice.DsoRules:DsoRules.DsoRules_ExpireSvOnboardingConfirmed: controlled by unchecked argument `sv` |
| High | Medium | `delegated-authority-leak` | `Splice/DsoRules.daml:993` | Splice.DsoRules:DsoRules.DsoRules_OnboardValidator: argument `validator` used with the signatories' authority |
| High | Medium | `delegated-authority-leak` | `Splice/DsoRules.daml:1037` | Splice.DsoRules:DsoRules.DsoRules_StartSvOnboarding: argument `candidateParty` used with the signatories' authority |
| Medium | High | `missing-ensure` | `Splice/DSO/SvState.daml:99` | Splice.DSO.SvState:SvStatusReport: no ensure constrains `number` |
| Medium | High | `missing-ensure` | `Splice/DsoBootstrap.daml:22` | Splice.DsoBootstrap:DsoBootstrap: no ensure constrains `sv1RewardWeight`, `amuletPrice` |
| Medium | High | `missing-ensure` | `Splice/DsoRules.daml:334` | Splice.DsoRules:Confirmation: no ensure constrains `expiresAt` |
| Medium | High | `missing-ensure` | `Splice/DsoRules.daml:316` | Splice.DsoRules:ElectionRequest: no ensure constrains `epoch` |
| Medium | High | `missing-ensure` | `Splice/SvOnboarding.daml:40` | Splice.SvOnboarding:SvOnboardingConfirmed: no ensure constrains `svRewardWeight`, `expiresAt` |
| Medium | High | `missing-ensure` | `Splice/SvOnboarding.daml:17` | Splice.SvOnboarding:SvOnboardingRequest: no ensure constrains `expiresAt` |
| Medium | Medium | `unbounded-input-loop` | `Splice/DsoRules.daml:1437` | Splice.DsoRules:DsoRules.DsoRules_AllocateUnallocatedUnclaimedActivityRecord: loop over argument `unclaimedRewardsToBurnCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/DsoRules.daml:617` | Splice.DsoRules:DsoRules.DsoRules_ElectDsoDelegate: loop over argument `requestCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/DsoRules.daml:890` | Splice.DsoRules:DsoRules.DsoRules_GarbageCollectAmuletPriceVotes: loop over argument `duplicateVoteCids`, `nonSvVoteCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/DsoRules.daml:1224` | Splice.DsoRules:DsoRules.DsoRules_ReceiveSvRewardCoupon: loop over argument `beneficiaries` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:1437` | Splice.DsoRules:DsoRules.DsoRules_AllocateUnallocatedUnclaimedActivityRecord: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:617` | Splice.DsoRules:DsoRules.DsoRules_ElectDsoDelegate: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:676` | Splice.DsoRules:DsoRules.DsoRules_ExecuteConfirmedAction: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:890` | Splice.DsoRules:DsoRules.DsoRules_GarbageCollectAmuletPriceVotes: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:1344` | Splice.DsoRules:DsoRules.DsoRules_MergeSvRewardState: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:1013` | Splice.DsoRules:DsoRules.DsoRules_MergeValidatorLicense: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/DsoRules.daml:1224` | Splice.DsoRules:DsoRules.DsoRules_ReceiveSvRewardCoupon: create inside a loop |
| Low | Medium | `missing-amount-check` | `Splice/DsoBootstrap.daml:22` | Splice.DsoBootstrap:DsoBootstrap: ensure does not check `amuletPrice` |
| Low | Medium | `partial-function` | `Splice/DsoRules.daml:479` | Splice.DsoRules:DsoRules.DsoRules_OffboardSv: argument reaches partial function: `sv` -> head |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:343` | Splice.DsoRules:Confirmation.Confirmation_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:741` | Splice.DsoRules:DsoRules.DsoRules_CastVote: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:790` | Splice.DsoRules:DsoRules.DsoRules_CloseVoteRequest: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:1417` | Splice.DsoRules:DsoRules.DsoRules_CreateUnallocatedUnclaimedActivityRecord: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:1361` | Splice.DsoRules:DsoRules.DsoRules_PruneAmuletConfigSchedule: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:1224` | Splice.DsoRules:DsoRules.DsoRules_ReceiveSvRewardCoupon: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:703` | Splice.DsoRules:DsoRules.DsoRules_RequestVote: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/DsoRules.daml:871` | Splice.DsoRules:DsoRules.DsoRules_UpdateAmuletPriceVote: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/SvOnboarding.daml:53` | Splice.SvOnboarding:SvOnboardingConfirmed.SvOnboardingConfirmed_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/SvOnboarding.daml:30` | Splice.SvOnboarding:SvOnboardingRequest.SvOnboardingRequest_Expire: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/DSO/SvState.daml:99` | Splice.DSO.SvState:SvStatusReport: no code reads `status` |
| Informational | Medium | `unused-template-field` | `Splice/DsoRules.daml:316` | Splice.DsoRules:ElectionRequest: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/DsoRules.daml:354` | Splice.DsoRules:VoteRequest: no code reads `requester`, `reason` |
| Informational | Medium | `unused-template-field` | `Splice/SvOnboarding.daml:40` | Splice.SvOnboarding:SvOnboardingConfirmed: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/SvOnboarding.daml:17` | Splice.SvOnboarding:SvOnboardingRequest: no code reads `candidateParticipantId`, `token`, `sponsor` |
