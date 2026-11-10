# splice-amulet-0.1.25

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-amulet 0.1.25 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 65

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | Medium | `controller-from-argument` | `Splice/AmuletRules.daml:2289` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Cancel: controlled by unchecked argument `*` |
| High | Medium | `controller-from-argument` | `Splice/ExternalPartyAmuletRules.daml:304` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Expire: controlled by unchecked argument `*` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:671` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Reject: archived by non-signatory controller `beneficiary` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:662` | Splice.Amulet:DevelopmentFundCoupon.DevelopmentFundCoupon_Withdraw: archived by non-signatory controller `fundManager` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:385` | Splice.Amulet:FeaturedAppRight.FeaturedAppRight_Cancel: archived by non-signatory controller `provider` |
| High | Medium | `unprotected-archive` | `Splice/Amulet.daml:623` | Splice.Amulet:SvRewardCoupon.SvRewardCoupon_ArchiveAsBeneficiary: archived by non-signatory controller `beneficiary` |
| High | Medium | `unprotected-archive` | `Splice/AmuletRules.daml:2105` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Accept: archived by non-signatory controller `user` |
| High | Medium | `unprotected-archive` | `Splice/AmuletRules.daml:2123` | Splice.AmuletRules:ExternalPartySetupProposal.ExternalPartySetupProposal_Reject: archived by non-signatory controller `user` |
| High | Medium | `unprotected-archive` | `Splice/ExternalPartyAmuletRules.daml:248` | Splice.ExternalPartyAmuletRules:TransferCommand.TransferCommand_Send: archived by non-signatory controller `delegate` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:126` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_Cancel: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:81` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:89` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_RecordValidatorLivenessActivity: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:153` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReportActive: archived by non-signatory controller `validator` |
| High | Medium | `unprotected-archive` | `Splice/ValidatorLicense.daml:133` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_UpdateMetadata: archived by non-signatory controller `validator` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TokenApiUtils.daml:303` | Splice.Amulet.TokenApiUtils:$$ctoAnyValue8: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Amulet/TwoStepTransfer.daml:52` | Splice.Amulet.TwoStepTransfer:holdingToTransferInputs: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/AmuletRules.daml:2465` | Splice.AmuletRules:getExternalPartyConfigStateFromChoiceContext: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/GovernanceLock/Substitution.daml:187` | Splice.GovernanceLock.Substitution:substitution_transferInstructionView: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/GovernanceLock/Substitution.daml:80` | c5203dee918350373a993328e345872113bd5f8c8f0f51967014d813e583ae66:Splice.GovernanceLock.Substitution:GovernanceLockSubstitution@29317e3b7b165d2bbf16721bcca0ec4869e53eddb2738bddf790d61af28e0099:Splice.Api.Token.TransferInstructionV2:TransferInstruction.view: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/GovernanceLock/Substitution.daml:57` | c5203dee918350373a993328e345872113bd5f8c8f0f51967014d813e583ae66:Splice.GovernanceLock.Substitution:GovernanceLockSubstitution@55ba4deb0ad4662c4168b39859738a0e91388d252286480c7331b3f71a517281:Splice.Api.Token.TransferInstructionV1:TransferInstruction.transferInstruction_acceptImpl: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/GovernanceLock/Substitution.daml:57` | c5203dee918350373a993328e345872113bd5f8c8f0f51967014d813e583ae66:Splice.GovernanceLock.Substitution:GovernanceLockSubstitution@55ba4deb0ad4662c4168b39859738a0e91388d252286480c7331b3f71a517281:Splice.Api.Token.TransferInstructionV1:TransferInstruction.transferInstruction_rejectImpl: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/GovernanceLock/Substitution.daml:57` | c5203dee918350373a993328e345872113bd5f8c8f0f51967014d813e583ae66:Splice.GovernanceLock.Substitution:GovernanceLockSubstitution@55ba4deb0ad4662c4168b39859738a0e91388d252286480c7331b3f71a517281:Splice.Api.Token.TransferInstructionV1:TransferInstruction.transferInstruction_withdrawImpl: unsafe primitive `coerceContractId` |
| Medium | High | `hardcoded-party` | `Splice/ExternalPartyAmuletRules.daml:349` | Splice.ExternalPartyAmuletRules:trafficPurchaseReceiver: party built from text literal "splice_traffic-manager::..." |
| Medium | High | `hardcoded-party` | `Splice/GovernanceLock.daml:796` | Splice.GovernanceLock:lockManagerParty: party built from text literal "_lock-manager::122000000..." |
| Medium | Medium | `ignored-optional` | `Splice/GovernanceLock/Substitution.daml:50` | Splice.GovernanceLock.Substitution:GovernanceLockSubstitution.GovernanceLockSubstitution_DsoExpire.update: `_` is never used |
| Medium | High | `missing-ensure` | `Splice/Amulet/RewardAccountingV2.daml:26` | Splice.Amulet.RewardAccountingV2:CalculateRewardsV2: no ensure constrains `roundClosedAt` |
| Medium | High | `missing-ensure` | `Splice/Amulet/RewardAccountingV2.daml:61` | Splice.Amulet.RewardAccountingV2:ProcessRewardsV2: no ensure constrains `roundClosedAt` |
| Medium | High | `missing-ensure` | `Splice/AmuletRules.daml:2094` | Splice.AmuletRules:ExternalPartySetupProposal: no ensure constrains `createdAt`, `preapprovalExpiresAt` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:229` | Splice.ExternalPartyAmuletRules:TransferCommand: no ensure constrains `amount`, `expiresAt`, `nonce` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyAmuletRules.daml:210` | Splice.ExternalPartyAmuletRules:TransferCommandCounter: no ensure constrains `nextNonce` |
| Medium | High | `missing-ensure` | `Splice/ExternalPartyConfigState.daml:24` | Splice.ExternalPartyConfigState:ExternalPartyConfigState: no ensure constrains `amuletPrice`, `targetArchiveAfter` |
| Medium | Medium | `stuck-asset` | `Splice/Amulet.daml:158` | Splice.Amulet:Amulet: `owner` controls no consuming choice except Archive |
| Medium | Medium | `stuck-asset` | `Splice/GovernanceLock/Substitution.daml:35` | Splice.GovernanceLock.Substitution:GovernanceLockSubstitution: `owner` controls no consuming choice except Archive |
| Medium | Medium | `stuck-asset` | `Splice/GovernanceLock.daml:158` | Splice.GovernanceLock:GovernanceLock: `owner` controls no consuming choice except Archive |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:292` | Splice.AmuletRules:AmuletRules.AmuletRules_BuyMemberTraffic: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:950` | Splice.AmuletRules:AmuletRules.AmuletRules_ConvertFeaturedAppActivityMarkers: exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:223` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateExternalPartySetupProposal: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:257` | Splice.AmuletRules:AmuletRules.AmuletRules_CreateTransferPreapproval: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:205` | Splice.AmuletRules:AmuletRules.AmuletRules_Transfer: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:2265` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_Renew: create, exercise, fetch inside a loop |
| Low | Medium | `ledger-op-in-loop` | `Splice/AmuletRules.daml:2219` | Splice.AmuletRules:TransferPreapproval.TransferPreapproval_SendV2: create, exercise, fetch inside a loop |
| Low | Medium | `missing-amount-check` | `Splice/ExternalPartyAmuletRules.daml:229` | Splice.ExternalPartyAmuletRules:TransferCommand: ensure does not check `amount` |
| Low | Medium | `missing-amount-check` | `Splice/ExternalPartyConfigState.daml:24` | Splice.ExternalPartyConfigState:ExternalPartyConfigState: ensure does not check `amuletPrice` |
| Low | Medium | `missing-amount-check` | `Splice/GovernanceLock/Substitution.daml:35` | Splice.GovernanceLock.Substitution:GovernanceLockSubstitution: ensure does not check `amount` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:92` | Splice.Round:ClosedMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:63` | Splice.Round:IssuingMiningRound: ensure does not check `issuancePerValidatorRewardCoupon`, `issuancePerFeaturedAppRewardCoupon`, `issuancePerUnfeaturedAppRewardCoupon`, `issuancePerSvRewardCoupon` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:20` | Splice.Round:OpenMiningRound: ensure does not check `amuletPrice` |
| Low | Medium | `missing-amount-check` | `Splice/Round.daml:49` | Splice.Round:SummarizingMiningRound: ensure does not check `amuletPrice` |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:167` | Splice.Amulet:Amulet.Amulet_Expire: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:257` | Splice.Amulet:LockedAmulet.LockedAmulet_ExpireAmulet: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:243` | Splice.Amulet:LockedAmulet.LockedAmulet_OwnerExpireLock: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/Amulet.daml:230` | Splice.Amulet:LockedAmulet.LockedAmulet_Unlock: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:925` | Splice.AmuletRules:AmuletRules.AmuletRules_AddFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:192` | Splice.AmuletRules:AmuletRules.AmuletRules_ComputeFees: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:934` | Splice.AmuletRules:AmuletRules.AmuletRules_RemoveFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/AmuletRules.daml:943` | Splice.AmuletRules:AmuletRules.AmuletRules_UpdateFutureAmuletConfigSchedule: every exercise aborts |
| Informational | High | `aborting-choice` | `Splice/ValidatorLicense.daml:81` | Splice.ValidatorLicense:ValidatorLicense.ValidatorLicense_ReceiveFaucetCoupon: every exercise aborts |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:640` | Splice.Amulet:DevelopmentFundCoupon: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:524` | Splice.Amulet:RewardCouponV2: no code reads `round` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:701` | Splice.Amulet:UnclaimedActivityRecord: no code reads `reason` |
| Informational | Medium | `unused-template-field` | `Splice/Amulet.daml:285` | Splice.Amulet:ValidatorRight: no code reads `dso` |
| Informational | Medium | `unused-template-field` | `Splice/ExternalPartyConfigState.daml:24` | Splice.ExternalPartyConfigState:ExternalPartyConfigState: no code reads `amuletSwitchOverTimes` |
| Informational | Medium | `unused-template-field` | `Splice/Round.daml:63` | Splice.Round:IssuingMiningRound: no code reads `optIssuancePerFeaturedAssetRewardCoupon` |
| Informational | Medium | `unused-template-field` | `Splice/Round.daml:49` | Splice.Round:SummarizingMiningRound: no code reads `trafficPrice`, `rewardConfig` |
| Informational | Medium | `unused-template-field` | `Splice/ValidatorLicense.daml:60` | Splice.ValidatorLicense:ValidatorLicense: no code reads `sponsor` |
