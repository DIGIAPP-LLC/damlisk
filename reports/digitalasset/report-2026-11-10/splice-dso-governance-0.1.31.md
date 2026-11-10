# splice-dso-governance-0.1.31

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-dso-governance 0.1.31 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 20

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/DsoRules.daml:776` | Splice.DsoRules:DsoRules.DsoRules_ElectDsoDelegate: controlled by unchecked argument `*` |
| High | Medium | `controller-from-argument` | `Splice/DsoRules.daml:1293` | Splice.DsoRules:DsoRules.DsoRules_ExpireSvOnboardingConfirmed: controlled by unchecked argument `*` |
| Medium | High | `missing-ensure` | `Splice/DSO/Instruction.daml:18` | Splice.DSO.Instruction:FeaturedAppConfigUpdateInstruction: no ensure constrains `expiresAt` |
| Medium | High | `missing-ensure` | `Splice/DSO/SvState.daml:99` | Splice.DSO.SvState:SvStatusReport: no ensure constrains `number` |
| Medium | High | `missing-ensure` | `Splice/DsoBootstrap.daml:24` | Splice.DsoBootstrap:DsoBootstrap: no ensure constrains `sv1RewardWeight`, `amuletPrice` |
| Medium | High | `missing-ensure` | `Splice/DsoRules.daml:479` | Splice.DsoRules:Confirmation: no ensure constrains `expiresAt` |
| Medium | High | `missing-ensure` | `Splice/DsoRules.daml:461` | Splice.DsoRules:ElectionRequest: no ensure constrains `epoch` |
| Medium | High | `missing-ensure` | `Splice/SvOnboarding.daml:42` | Splice.SvOnboarding:SvOnboardingConfirmed: no ensure constrains `svRewardWeight`, `expiresAt` |
| Medium | High | `missing-ensure` | `Splice/SvOnboarding.daml:19` | Splice.SvOnboarding:SvOnboardingRequest: no ensure constrains `expiresAt` |
| Low | Medium | `missing-amount-check` | `Splice/DsoBootstrap.daml:24` | Splice.DsoBootstrap:DsoBootstrap: ensure does not check `amuletPrice` |
| Informational | High | `aborting-choice` | `Splice/DsoRules.daml:1352` | Splice.DsoRules:DsoRules.DsoRules_Amulet_Expire: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/DsoRules.daml:787` | Splice.DsoRules:DsoRules.DsoRules_ArchiveOutdatedElectionRequest: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/DsoRules.daml:776` | Splice.DsoRules:DsoRules.DsoRules_ElectDsoDelegate: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/DsoRules.daml:1819` | Splice.DsoRules:DsoRules.DsoRules_PruneAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/DsoRules.daml:766` | Splice.DsoRules:DsoRules.DsoRules_RequestElection: every exercise aborts |
| Informational | Medium | `unused-template-field` | `Splice/DSO/SvState.daml:99` | Splice.DSO.SvState:SvStatusReport: no code reads `status` |
| Informational | Medium | `unused-template-field` | `Splice/DsoRules.daml:461` | Splice.DsoRules:ElectionRequest: no code reads `requester`, `epoch`, `reason`, `ranking` |
| Informational | Medium | `unused-template-field` | `Splice/DsoRules.daml:498` | Splice.DsoRules:VoteRequest: no code reads `requester`, `reason` |
| Informational | Medium | `unused-template-field` | `Splice/SvOnboarding.daml:42` | Splice.SvOnboarding:SvOnboardingConfirmed: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/SvOnboarding.daml:19` | Splice.SvOnboarding:SvOnboardingRequest: no code reads `candidateParticipantId`, `token`, `sponsor` |
