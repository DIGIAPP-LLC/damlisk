# splice-amulet-0.1.22

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-amulet 0.1.22 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 114

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `delegated-authority-leak` | `Splice/AmuletRules.daml:815` | Splice.AmuletRules:AmuletRules.AmuletRules_AllocateDevelopmentFundCoupon: argument `beneficiary` used with the signatories' authority |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:571` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Reject: archived by non-signatory controller `beneficiary` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:562` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Withdraw: archived by non-signatory controller `fundManager` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:311` | Splice.Amulet:FeaturedAppRight.FeaturedAppRight_Cancel: archived by non-signatory controller `provider` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:524` | Splice.Amulet:SvRewardCoupon.SvRewardCoupon_ArchiveAsBeneficiary: archived by non-signatory controller `beneficiary` |
| High | Medium | `unprotected-archive` | `Splice/AmuletRules.daml:1987` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Accept: archived by non-signatory controller `user` |
| High | Medium | `unprotected-archive` | `Splice/AmuletRules.daml:2005` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Reject: archived by non-signatory controller `user` |
| High | Medium | `unprotected-archive` | `Splice/ExternalPartyAmuletRules.daml:242` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Send: archived by non-signatory controller `delegate` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:118` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_Cancel: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:73` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:81` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_RecordValidatorLivenessActivity: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:145` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReportActive: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:125` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_UpdateMetadata: archived by non-signatory controller `validator` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TokenApiUtils.daml:283` | Splice.Amulet.TokenApiUtils:$$ctoAnyValue8: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TwoStepTransfer.daml:60` | Splice.Amulet.TwoStepTransfer:holdingToTransferInputs: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TokenApiUtils.daml:327` | Splice.AmuletRules:getExternalPartyConfigStateFromChoiceContext: unsafe primitive `coerceContractId` |
| Medium | Medium | `divide-before-multiply` | `Splice/AmuletRules.daml:906` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers.update: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/AmuletRules.daml:1734` | Splice.AmuletRules:computeSynchronizerFees: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Fees.daml:171` | Splice.Fees:ratePerRoundToRatePerDay: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:187` | Splice.Issuance:computeIssuanceTranche: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:128` | Splice.Issuance:computeIssuingRoundParameters: result of a division is multiplied |
| Medium | High | `missing-ensure` | `Splice/Amulet/RewardAccountingV2.daml:26` | Splice.Amulet.RewardAccountingV2:CalculateRewardsV2: no ensure constrains `roundClosedAt` |
| Medium | High | `missing-ensure` | `Splice/Amulet/RewardAccountingV2.daml:61` | Splice.Amulet.RewardAccountingV2:ProcessRewardsV2: no ensure constrains `roundClosedAt` |
| Medium | High | `missing-ensure` | `Splice/AmuletRules.daml:1976` | Splice.AmuletRules:ExternalPartySetupProposal: no ensure constrains `createdAt`, `preapprovalExpiresAt` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:223` | Splice.ExternalPartyAmuletRules:TransferCommand: no ensure constrains `amount`, `expiresAt`, `nonce` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:204` | Splice.ExternalPartyAmuletRules:TransferCommandCounter: no ensure constrains `nextNonce` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyConfigState.daml:22` | Splice.ExternalPartyConfigState:ExternalPartyConfigState: no ensure constrains `amuletPrice`, `targetArchiveAfter` |
| Medium | Medium | `over-disclosure` | `Splice/Amulet/RewardAccountingV2.daml:75` | Splice.Amulet.RewardAccountingV2:ProcessRewardsV2.ProcessRewardsV2_ProcessBatch: choice observers taken from argument `batch`, `providersWithWrongVettingState` |
| Medium | Medium | `over-disclosure` | `Splice/AmuletRules.daml:942` | Splice.AmuletRules:AmuletRules.AmuletRules_Amulet_ExpireTransferInstructions: choice observers taken from argument `observers` |
| Medium | Medium | `over-disclosure` | `Splice/AmuletRules.daml:697` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewardsV2: choice observers taken from argument `expiryObservers` |
| Medium | Medium | `over-disclosure` | `Splice/AmuletRules.daml:906` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: choice observers taken from argument `observers` |
| Medium | Medium | `over-disclosure` | `Splice/AmuletRules.daml:738` | Splice.AmuletRules:AmuletRules.AmuletRules_UnhideRewardCouponsV2: choice observers taken from argument `providers` |
| Medium | Medium | `over-disclosure` | `Splice/ExternalPartyAmuletRules.daml:59` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_ExpireAmuletAllocations: choice observers taken from argument `observers` |
| Medium | Medium | `over-disclosure` | `Splice/ExternalPartyAmuletRules.daml:77` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_ExpireAmuletAllocationsV2: choice observers taken from argument `observers` |
| Medium | Medium | `stuck-asset` | `Splice/Amulet.daml:132` | Splice.Amulet:Amulet: `owner` controls no consuming choice except Archive |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:815` | Splice.AmuletRules:AmuletRules.AmuletRules_AllocateDevelopmentFundCoupon: loop over argument `unclaimedDevelopmentFundCouponCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:942` | Splice.AmuletRules:AmuletRules.AmuletRules_Amulet_ExpireTransferInstructions: loop over argument `inputs` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:761` | Splice.AmuletRules:AmuletRules.AmuletRules_ArchiveDryRunRewardAccountingV2: loop over argument `calculateRewardsCids`, `processRewardsCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:637` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewards: loop over argument `appCouponCids`, `optValidatorFaucetCouponCids`, `optValidatorLivenessActivityRecordCids`, `svRewardCouponCids`, `validatorRewardCouponCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:697` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewardsV2: loop over argument `rewardCouponCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:906` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: loop over argument `markerCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:309` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeMemberTrafficContracts: loop over argument `trafficCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:738` | Splice.AmuletRules:AmuletRules.AmuletRules_UnhideRewardCouponsV2: loop over argument `rewardCouponCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/ExternalPartyAmuletRules.daml:59` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_ExpireAmuletAllocations: loop over argument `inputs` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/ExternalPartyAmuletRules.daml:77` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_ExpireAmuletAllocationsV2: loop over argument `cancellations` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/Amulet/RewardAccountingV2.daml:75` | Splice.Amulet.RewardAccountingV2:ProcessRewardsV2.ProcessRewardsV2_ProcessBatch: create inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:484` | Splice.AmuletRules:AmuletRules.AmuletRules_AdvanceOpenMiningRounds: create inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:815` | Splice.AmuletRules:AmuletRules.AmuletRules_AllocateDevelopmentFundCoupon: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:942` | Splice.AmuletRules:AmuletRules.AmuletRules_Amulet_ExpireTransferInstructions: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:761` | Splice.AmuletRules:AmuletRules.AmuletRules_ArchiveDryRunRewardAccountingV2: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:266` | Splice.AmuletRules:AmuletRules.AmuletRules_BuyMemberTraffic: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:637` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewards: exercise inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:697` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewardsV2: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:906` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:197` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateExternalPartySetupProposal: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:231` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateTransferPreapproval: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:309` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeMemberTrafficContracts: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:795` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeUnclaimedDevelopmentFundCoupons: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:776` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeUnclaimedRewards: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:181` | Splice.AmuletRules:AmuletRules.AmuletRules_Transfer: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:738` | Splice.AmuletRules:AmuletRules.AmuletRules_UnhideRewardCouponsV2: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:2147` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Renew: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:2101` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_SendV2: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/ExternalPartyAmuletRules.daml:59` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_ExpireAmuletAllocations: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/ExternalPartyAmuletRules.daml:77` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_ExpireAmuletAllocationsV2: exercise, fetch inside a loop |
| Low | Medium | `missing-amount-check` | `Splice/ExternalPartyAmuletRules.daml:223` | Splice.ExternalPartyAmuletRules:TransferCommand: ensure does not check `amount` |
| Low | Medium | `missing-amount-check` | `Splice/ExternalPartyConfigState.daml:22` | Splice.ExternalPartyConfigState:ExternalPartyConfigState: ensure does not check `amuletPrice` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:86` | Splice.Round:ClosedMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:63` | Splice.Round:IssuingMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:20` | Splice.Round:OpenMiningRound: ensure does not check `amuletPrice` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:49` | Splice.Round:SummarizingMiningRound: ensure does not check `amuletPrice` |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:580` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_DsoExpire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:571` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Reject: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:562` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Withdraw: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:223` | Splice.Amulet:LockedAmulet.LockedAmulet_OwnerExpireLockV2: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:613` | Splice.Amulet:UnclaimedActivityRecord.UnclaimedActivityRecord_DsoExpire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletAllocation.daml:134` | Splice.AmuletAllocation:AmuletAllocation.AmuletAllocation_DsoExpire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:484` | Splice.AmuletRules:AmuletRules.AmuletRules_AdvanceOpenMiningRounds: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:815` | Splice.AmuletRules:AmuletRules.AmuletRules_AllocateDevelopmentFundCoupon: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:474` | Splice.AmuletRules:AmuletRules.AmuletRules_BootstrapExternalPartyConfigState: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:409` | Splice.AmuletRules:AmuletRules.AmuletRules_Bootstrap_Rounds: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:266` | Splice.AmuletRules:AmuletRules.AmuletRules_BuyMemberTraffic: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:906` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:197` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateExternalPartySetupProposal: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:231` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateTransferPreapproval: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:606` | Splice.AmuletRules:AmuletRules.AmuletRules_MiningRound_Close: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:968` | Splice.AmuletRules:AmuletRules.AmuletRules_UpdateExternalPartyConfigStates: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1987` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Accept: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:2171` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Cancel: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:2164` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:2147` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Renew: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:2064` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Send: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:2101` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_SendV2: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:102` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_CreateTransferCommand: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:298` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:242` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Send: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:81` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_RecordValidatorLivenessActivity: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:145` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReportActive: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:125` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_UpdateMetadata: ledger time decides a branch |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:141` | Splice.Amulet:Amulet.Amulet_Expire: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:231` | Splice.Amulet:LockedAmulet.LockedAmulet_ExpireAmulet: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:217` | Splice.Amulet:LockedAmulet.LockedAmulet_OwnerExpireLock: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:204` | Splice.Amulet:LockedAmulet.LockedAmulet_Unlock: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:881` | Splice.AmuletRules:AmuletRules.AmuletRules_AddFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:168` | Splice.AmuletRules:AmuletRules.AmuletRules_ComputeFees: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:890` | Splice.AmuletRules:AmuletRules.AmuletRules_RemoveFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:899` | Splice.AmuletRules:AmuletRules.AmuletRules_UpdateFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/ValidatorLicense.daml:73` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: every exercise aborts |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:541` | Splice.Amulet:DevelopmentFundCoupon: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:425` | Splice.Amulet:RewardCouponV2: no code reads `round` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:601` | Splice.Amulet:UnclaimedActivityRecord: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:259` | Splice.Amulet:ValidatorRight: no code reads `dso` |
| Informational | Medium | `unused-template-field` | `Splice/Round.daml:49` | Splice.Round:SummarizingMiningRound: no code reads `trafficPrice`, `rewardConfig` |
| Informational | Medium | `unused-template-field` | `Splice/ValidatorLicense.daml:52` | Splice.ValidatorLicense:ValidatorLicense: no code reads `sponsor` |
