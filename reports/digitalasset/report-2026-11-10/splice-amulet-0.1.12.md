# splice-amulet-0.1.12

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-amulet 0.1.12 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 71

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:227` | Splice.Amulet:FeaturedAppRight.FeaturedAppRight_Cancel: archived by non-signatory controller `provider` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:379` | Splice.Amulet:SvRewardCoupon.SvRewardCoupon_ArchiveAsBeneficiary: archived by non-signatory controller `beneficiary` |
| High | Medium | `unprotected-archive` | `Splice/AmuletRules.daml:1382` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Accept: archived by non-signatory controller `user` |
| High | Medium | `unprotected-archive` | `Splice/AmuletRules.daml:1400` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Reject: archived by non-signatory controller `user` |
| High | Medium | `unprotected-archive` | `Splice/ExternalPartyAmuletRules.daml:133` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Send: archived by non-signatory controller `delegate` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:111` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_Cancel: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:66` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:74` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_RecordValidatorLivenessActivity: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:137` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReportActive: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:118` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_UpdateMetadata: archived by non-signatory controller `validator` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TokenApiUtils.daml:284` | Splice.Amulet.TokenApiUtils:$$ctoAnyValue8: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TwoStepTransfer.daml:71` | Splice.Amulet.TwoStepTransfer:holdingToTransferInputs: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TokenApiUtils.daml:328` | Splice.AmuletRules:paymentFromChoiceContext: unsafe primitive `coerceContractId` |
| Medium | Medium | `divide-before-multiply` | `Splice/AmuletRules.daml:626` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers.update: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/AmuletRules.daml:1147` | Splice.AmuletRules:computeSynchronizerFees: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Fees.daml:181` | Splice.Fees:ratePerRoundToRatePerDay: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:169` | Splice.Issuance:computeIssuanceTranche: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:118` | Splice.Issuance:computeIssuingRoundParameters: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:129` | Splice.Issuance:computeIssuingRoundParameters: result of a division is multiplied |
| Medium | High | `missing-ensure` | `Splice/AmuletRules.daml:1371` | Splice.AmuletRules:ExternalPartySetupProposal: no ensure constrains `createdAt`, `preapprovalExpiresAt` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:114` | Splice.ExternalPartyAmuletRules:TransferCommand: no ensure constrains `amount`, `expiresAt`, `nonce` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:93` | Splice.ExternalPartyAmuletRules:TransferCommandCounter: no ensure constrains `nextNonce` |
| Medium | Medium | `stuck-asset` | `Splice/Amulet.daml:89` | Splice.Amulet:Amulet: `owner` controls no consuming choice except Archive |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:498` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewards: loop over argument `appCouponCids`, `optValidatorFaucetCouponCids`, `optValidatorLivenessActivityRecordCids`, `svRewardCouponCids`, `validatorRewardCouponCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:626` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: loop over argument `markerCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:245` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeMemberTrafficContracts: loop over argument `trafficCids` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:199` | Splice.AmuletRules:AmuletRules.AmuletRules_BuyMemberTraffic: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:498` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewards: exercise inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:626` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:136` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateExternalPartySetupProposal: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:166` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateTransferPreapproval: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:245` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeMemberTrafficContracts: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:558` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeUnclaimedRewards: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:120` | Splice.AmuletRules:AmuletRules.AmuletRules_Transfer: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:1493` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Renew: create, exercise, fetch inside a loop |
| Low | Medium | `missing-amount-check` | `Splice/ExternalPartyAmuletRules.daml:114` | Splice.ExternalPartyAmuletRules:TransferCommand: ensure does not check `amount` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:78` | Splice.Round:ClosedMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:55` | Splice.Round:IssuingMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:20` | Splice.Round:OpenMiningRound: ensure does not check `amuletPrice` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:43` | Splice.Round:SummarizingMiningRound: ensure does not check `amuletPrice` |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:174` | Splice.Amulet:LockedAmulet.LockedAmulet_ExpireAmulet: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:160` | Splice.Amulet:LockedAmulet.LockedAmulet_OwnerExpireLock: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:409` | Splice.Amulet:UnclaimedActivityRecord.UnclaimedActivityRecord_DsoExpire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:379` | Splice.AmuletRules:AmuletRules.AmuletRules_AdvanceOpenMiningRounds: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:333` | Splice.AmuletRules:AmuletRules.AmuletRules_Bootstrap_Rounds: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:199` | Splice.AmuletRules:AmuletRules.AmuletRules_BuyMemberTraffic: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:626` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:136` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateExternalPartySetupProposal: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:166` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateTransferPreapproval: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:467` | Splice.AmuletRules:AmuletRules.AmuletRules_MiningRound_Close: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1382` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Accept: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1521` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Cancel: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1514` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1493` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Renew: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1461` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Send: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:38` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_CreateTransferCommand: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:205` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:133` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Send: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:74` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_RecordValidatorLivenessActivity: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:137` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReportActive: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:118` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_UpdateMetadata: ledger time decides a branch |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:601` | Splice.AmuletRules:AmuletRules.AmuletRules_AddFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:610` | Splice.AmuletRules:AmuletRules.AmuletRules_RemoveFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:619` | Splice.AmuletRules:AmuletRules.AmuletRules_UpdateFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/ValidatorLicense.daml:66` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: every exercise aborts |
| Informational | High | `debug-trace` | `Splice/AmuletRules.daml:1005` | Splice.AmuletRules:summarizeTransfer: debug output `trace` |
| Informational | High | `debug-trace` | `Splice/AmuletRules.daml:1005` | Splice.AmuletRules:summarizeTransfer: debug output `trace` |
| Informational | High | `debug-trace` | `Splice/AmuletRules.daml:1005` | Splice.AmuletRules:summarizeTransfer: debug output `trace` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:397` | Splice.Amulet:UnclaimedActivityRecord: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:195` | Splice.Amulet:ValidatorRight: no code reads `dso` |
| Informational | Medium | `unused-template-field` | `Splice/ValidatorLicense.daml:52` | Splice.ValidatorLicense:ValidatorLicense: no code reads `sponsor` |
