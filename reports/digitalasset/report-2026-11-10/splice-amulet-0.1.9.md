# splice-amulet-0.1.9

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-amulet 0.1.9 (LF 2.1)
- **SDK:** 3.3.0-snapshot.20250502.13767.0.v2fc6c7e2
- **Findings:** 66

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:222` | Splice.Amulet:FeaturedAppRight.FeaturedAppRight_Cancel: archived by non-signatory controller `provider` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:374` | Splice.Amulet:SvRewardCoupon.SvRewardCoupon_ArchiveAsBeneficiary: archived by non-signatory controller `beneficiary` |
| High | Medium | `unprotected-archive` | `Splice/AmuletRules.daml:1323` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Accept: archived by non-signatory controller `user` |
| High | Medium | `unprotected-archive` | `Splice/ExternalPartyAmuletRules.daml:129` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Send: archived by non-signatory controller `delegate` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:111` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_Cancel: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:66` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:74` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_RecordValidatorLivenessActivity: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:137` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReportActive: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:118` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_UpdateMetadata: archived by non-signatory controller `validator` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TokenApiUtils.daml:275` | Splice.Amulet.TokenApiUtils:$$ctoAnyValue8: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TwoStepTransfer.daml:71` | Splice.Amulet.TwoStepTransfer:holdingToTransferInputs: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TokenApiUtils.daml:319` | Splice.AmuletRules:paymentFromChoiceContext: unsafe primitive `coerceContractId` |
| Medium | Medium | `divide-before-multiply` | `Splice/AmuletRules.daml:603` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers.update: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/AmuletRules.daml:1095` | Splice.AmuletRules:computeSynchronizerFees: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Fees.daml:162` | Splice.Fees:ratePerRoundToRatePerDay: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:168` | Splice.Issuance:computeIssuanceTranche: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:117` | Splice.Issuance:computeIssuingRoundParameters: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:128` | Splice.Issuance:computeIssuingRoundParameters: result of a division is multiplied |
| Medium | High | `missing-ensure` | `Splice/AmuletRules.daml:1312` | Splice.AmuletRules:ExternalPartySetupProposal: no ensure constrains `createdAt`, `preapprovalExpiresAt` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:110` | Splice.ExternalPartyAmuletRules:TransferCommand: no ensure constrains `amount`, `expiresAt`, `nonce` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:89` | Splice.ExternalPartyAmuletRules:TransferCommandCounter: no ensure constrains `nextNonce` |
| Medium | Medium | `stuck-asset` | `Splice/Amulet.daml:84` | Splice.Amulet:Amulet: `owner` controls no consuming choice except Archive |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:468` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewards: loop over argument `appCouponCids`, `optValidatorFaucetCouponCids`, `optValidatorLivenessActivityRecordCids`, `svRewardCouponCids`, `validatorRewardCouponCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:603` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: loop over argument `markerCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:218` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeMemberTrafficContracts: loop over argument `trafficCids` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:177` | Splice.AmuletRules:AmuletRules.AmuletRules_BuyMemberTraffic: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:468` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewards: exercise inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:603` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:124` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateExternalPartySetupProposal: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:149` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateTransferPreapproval: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:218` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeMemberTrafficContracts: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:528` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeUnclaimedRewards: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:113` | Splice.AmuletRules:AmuletRules.AmuletRules_Transfer: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:1409` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Renew: create, exercise, fetch inside a loop |
| Low | Medium | `missing-amount-check` | `Splice/ExternalPartyAmuletRules.daml:110` | Splice.ExternalPartyAmuletRules:TransferCommand: ensure does not check `amount` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:78` | Splice.Round:ClosedMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:55` | Splice.Round:IssuingMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:20` | Splice.Round:OpenMiningRound: ensure does not check `amuletPrice` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:43` | Splice.Round:SummarizingMiningRound: ensure does not check `amuletPrice` |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:169` | Splice.Amulet:LockedAmulet.LockedAmulet_ExpireAmulet: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:155` | Splice.Amulet:LockedAmulet.LockedAmulet_OwnerExpireLock: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:571` | Splice.AmuletRules:AmuletRules.AmuletRules_AddFutureAmuletConfigSchedule: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:349` | Splice.AmuletRules:AmuletRules.AmuletRules_AdvanceOpenMiningRounds: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:303` | Splice.AmuletRules:AmuletRules.AmuletRules_Bootstrap_Rounds: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:177` | Splice.AmuletRules:AmuletRules.AmuletRules_BuyMemberTraffic: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:603` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:124` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateExternalPartySetupProposal: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:149` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateTransferPreapproval: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:437` | Splice.AmuletRules:AmuletRules.AmuletRules_MiningRound_Close: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:582` | Splice.AmuletRules:AmuletRules.AmuletRules_RemoveFutureAmuletConfigSchedule: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:593` | Splice.AmuletRules:AmuletRules.AmuletRules_UpdateFutureAmuletConfigSchedule: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1437` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Cancel: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1430` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1409` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Renew: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1376` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Send: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:202` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:129` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Send: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:74` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_RecordValidatorLivenessActivity: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:137` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReportActive: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:118` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_UpdateMetadata: ledger time decides a branch |
| Informational | High | `aborting-choice` | `Splice/ValidatorLicense.daml:66` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: every exercise aborts |
| Informational | High | `debug-trace` | `Splice/AmuletRules.daml:955` | Splice.AmuletRules:summarizeTransfer: debug output `trace` |
| Informational | High | `debug-trace` | `Splice/AmuletRules.daml:955` | Splice.AmuletRules:summarizeTransfer: debug output `trace` |
| Informational | High | `debug-trace` | `Splice/AmuletRules.daml:955` | Splice.AmuletRules:summarizeTransfer: debug output `trace` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:190` | Splice.Amulet:ValidatorRight: no code reads `dso` |
| Informational | Medium | `unused-template-field` | `Splice/ValidatorLicense.daml:52` | Splice.ValidatorLicense:ValidatorLicense: no code reads `sponsor` |
