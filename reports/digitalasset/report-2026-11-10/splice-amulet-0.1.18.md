# splice-amulet-0.1.18

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-amulet 0.1.18 (LF 2.1)
- **SDK:** 3.4.11
- **Findings:** 99

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `delegated-authority-leak` | `Splice/AmuletRules.daml:655` | Splice.AmuletRules:AmuletRules.AmuletRules_AllocateDevelopmentFundCoupon: argument `beneficiary` used with the signatories' authority |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:490` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Reject: archived by non-signatory controller `beneficiary` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:481` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Withdraw: archived by non-signatory controller `fundManager` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:266` | Splice.Amulet:FeaturedAppRight.FeaturedAppRight_Cancel: archived by non-signatory controller `provider` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:443` | Splice.Amulet:SvRewardCoupon.SvRewardCoupon_ArchiveAsBeneficiary: archived by non-signatory controller `beneficiary` |
| High | Medium | `unprotected-archive` | `Splice/AmuletRules.daml:1699` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Accept: archived by non-signatory controller `user` |
| High | Medium | `unprotected-archive` | `Splice/AmuletRules.daml:1717` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Reject: archived by non-signatory controller `user` |
| High | Medium | `unprotected-archive` | `Splice/ExternalPartyAmuletRules.daml:160` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Send: archived by non-signatory controller `delegate` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:111` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_Cancel: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:66` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:74` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_RecordValidatorLivenessActivity: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:137` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReportActive: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:118` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_UpdateMetadata: archived by non-signatory controller `validator` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TokenApiUtils.daml:274` | Splice.Amulet.TokenApiUtils:$$ctoAnyValue8: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TwoStepTransfer.daml:59` | Splice.Amulet.TwoStepTransfer:holdingToTransferInputs: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TokenApiUtils.daml:318` | Splice.AmuletRules:externalPartyTransferFromChoiceContext: unsafe primitive `coerceContractId` |
| Medium | Medium | `divide-before-multiply` | `Splice/AmuletRules.daml:746` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers.update: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/AmuletRules.daml:1448` | Splice.AmuletRules:computeSynchronizerFees: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Fees.daml:171` | Splice.Fees:ratePerRoundToRatePerDay: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:187` | Splice.Issuance:computeIssuanceTranche: result of a division is multiplied |
| Medium | Medium | `divide-before-multiply` | `Splice/Issuance.daml:128` | Splice.Issuance:computeIssuingRoundParameters: result of a division is multiplied |
| Medium | High | `missing-ensure` | `Splice/AmuletRules.daml:1688` | Splice.AmuletRules:ExternalPartySetupProposal: no ensure constrains `createdAt`, `preapprovalExpiresAt` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:141` | Splice.ExternalPartyAmuletRules:TransferCommand: no ensure constrains `amount`, `expiresAt`, `nonce` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:122` | Splice.ExternalPartyAmuletRules:TransferCommandCounter: no ensure constrains `nextNonce` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyConfigState.daml:17` | Splice.ExternalPartyConfigState:ExternalPartyConfigState: no ensure constrains `amuletPrice`, `targetArchiveAfter` |
| Medium | Medium | `over-disclosure` | `Splice/AmuletRules.daml:775` | Splice.AmuletRules:AmuletRules.AmuletRules_Amulet_ExpireTransferInstructions: choice observers taken from argument `observers` |
| Medium | Medium | `over-disclosure` | `Splice/AmuletRules.daml:746` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: choice observers taken from argument `observers` |
| Medium | Medium | `over-disclosure` | `Splice/ExternalPartyAmuletRules.daml:45` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_ExpireAmuletAllocations: choice observers taken from argument `observers` |
| Medium | Medium | `stuck-asset` | `Splice/Amulet.daml:123` | Splice.Amulet:Amulet: `owner` controls no consuming choice except Archive |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:655` | Splice.AmuletRules:AmuletRules.AmuletRules_AllocateDevelopmentFundCoupon: loop over argument `unclaimedDevelopmentFundCouponCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:775` | Splice.AmuletRules:AmuletRules.AmuletRules_Amulet_ExpireTransferInstructions: loop over argument `inputs` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:556` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewards: loop over argument `appCouponCids`, `optValidatorFaucetCouponCids`, `optValidatorLivenessActivityRecordCids`, `svRewardCouponCids`, `validatorRewardCouponCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:746` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: loop over argument `markerCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/AmuletRules.daml:275` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeMemberTrafficContracts: loop over argument `trafficCids` with no length check |
| Medium | Medium | `unbounded-input-loop` | `Splice/ExternalPartyAmuletRules.daml:45` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_ExpireAmuletAllocations: loop over argument `inputs` with no length check |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:655` | Splice.AmuletRules:AmuletRules.AmuletRules_AllocateDevelopmentFundCoupon: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:775` | Splice.AmuletRules:AmuletRules.AmuletRules_Amulet_ExpireTransferInstructions: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:232` | Splice.AmuletRules:AmuletRules.AmuletRules_BuyMemberTraffic: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:556` | Splice.AmuletRules:AmuletRules.AmuletRules_ClaimExpiredRewards: exercise inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:746` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:169` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateExternalPartySetupProposal: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:199` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateTransferPreapproval: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:275` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeMemberTrafficContracts: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:635` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeUnclaimedDevelopmentFundCoupons: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:616` | Splice.AmuletRules:AmuletRules.AmuletRules_MergeUnclaimedRewards: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:153` | Splice.AmuletRules:AmuletRules.AmuletRules_Transfer: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:1842` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Renew: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:1810` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_SendV2: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/ExternalPartyAmuletRules.daml:45` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_ExpireAmuletAllocations: exercise, fetch inside a loop |
| Low | Medium | `missing-amount-check` | `Splice/ExternalPartyAmuletRules.daml:141` | Splice.ExternalPartyAmuletRules:TransferCommand: ensure does not check `amount` |
| Low | Medium | `missing-amount-check` | `Splice/ExternalPartyConfigState.daml:17` | Splice.ExternalPartyConfigState:ExternalPartyConfigState: ensure does not check `amuletPrice` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:78` | Splice.Round:ClosedMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:55` | Splice.Round:IssuingMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:20` | Splice.Round:OpenMiningRound: ensure does not check `amuletPrice` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:43` | Splice.Round:SummarizingMiningRound: ensure does not check `amuletPrice` |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:499` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_DsoExpire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:490` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Reject: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:481` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Withdraw: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:203` | Splice.Amulet:LockedAmulet.LockedAmulet_OwnerExpireLockV2: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/Amulet.daml:532` | Splice.Amulet:UnclaimedActivityRecord.UnclaimedActivityRecord_DsoExpire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletAllocation.daml:66` | Splice.AmuletAllocation:AmuletAllocation.AmuletAllocation_DsoExpire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:431` | Splice.AmuletRules:AmuletRules.AmuletRules_AdvanceOpenMiningRounds: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:655` | Splice.AmuletRules:AmuletRules.AmuletRules_AllocateDevelopmentFundCoupon: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:421` | Splice.AmuletRules:AmuletRules.AmuletRules_BootstrapExternalPartyConfigState: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:364` | Splice.AmuletRules:AmuletRules.AmuletRules_Bootstrap_Rounds: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:232` | Splice.AmuletRules:AmuletRules.AmuletRules_BuyMemberTraffic: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:746` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:169` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateExternalPartySetupProposal: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:199` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateTransferPreapproval: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:525` | Splice.AmuletRules:AmuletRules.AmuletRules_MiningRound_Close: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:801` | Splice.AmuletRules:AmuletRules.AmuletRules_UpdateExternalPartyConfigStates: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1699` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Accept: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1870` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Cancel: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1863` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1842` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Renew: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1777` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Send: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/AmuletRules.daml:1810` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_SendV2: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:67` | Splice.ExternalPartyAmuletRules:ExternalPartyAmuletRules.ExternalPartyAmuletRules_CreateTransferCommand: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:216` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Expire: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ExternalPartyAmuletRules.daml:160` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Send: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:74` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_RecordValidatorLivenessActivity: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:137` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReportActive: ledger time decides a branch |
| Low | Medium | `time-dependence` | `Splice/ValidatorLicense.daml:118` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_UpdateMetadata: ledger time decides a branch |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:132` | Splice.Amulet:Amulet.Amulet_Expire: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:210` | Splice.Amulet:LockedAmulet.LockedAmulet_ExpireAmulet: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:197` | Splice.Amulet:LockedAmulet.LockedAmulet_OwnerExpireLock: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:185` | Splice.Amulet:LockedAmulet.LockedAmulet_Unlock: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:721` | Splice.AmuletRules:AmuletRules.AmuletRules_AddFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:140` | Splice.AmuletRules:AmuletRules.AmuletRules_ComputeFees: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:730` | Splice.AmuletRules:AmuletRules.AmuletRules_RemoveFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:739` | Splice.AmuletRules:AmuletRules.AmuletRules_UpdateFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/ValidatorLicense.daml:66` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: every exercise aborts |
| Informational | High | `debug-trace` | `Splice/AmuletRules.daml:1312` | Splice.AmuletRules:summarizeTransfer: debug output `trace` |
| Informational | High | `debug-trace` | `Splice/AmuletRules.daml:1312` | Splice.AmuletRules:summarizeTransfer: debug output `trace` |
| Informational | High | `debug-trace` | `Splice/AmuletRules.daml:1312` | Splice.AmuletRules:summarizeTransfer: debug output `trace` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:460` | Splice.Amulet:DevelopmentFundCoupon: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:520` | Splice.Amulet:UnclaimedActivityRecord: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:234` | Splice.Amulet:ValidatorRight: no code reads `dso` |
| Informational | Medium | `unused-template-field` | `Splice/ValidatorLicense.daml:52` | Splice.ValidatorLicense:ValidatorLicense: no code reads `sponsor` |
