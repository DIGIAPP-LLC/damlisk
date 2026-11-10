# splice-test-token-v2-1.0.1

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-test-token-v2 1.0.1 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 17

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:603` | 6f2bddc934eb700ee00afa209eb1d49f861af6401037618f6aa7e6ac02c8e201:Splice.Testing.Tokens.TestTokenV2.Allocation:TokenAllocationV1@93c942ae2b4c2ba674fb152fe38473c507bda4e82b4e4c5da55a552a9d8cce1d:Splice.Api.Token.AllocationV1:Allocation.allocation_executeTransferImpl: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:604` | 6f2bddc934eb700ee00afa209eb1d49f861af6401037618f6aa7e6ac02c8e201:Splice.Testing.Tokens.TestTokenV2.Allocation:TokenAllocationV1@93c942ae2b4c2ba674fb152fe38473c507bda4e82b4e4c5da55a552a9d8cce1d:Splice.Api.Token.AllocationV1:Allocation.allocation_executeTransferImpl: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:610` | 6f2bddc934eb700ee00afa209eb1d49f861af6401037618f6aa7e6ac02c8e201:Splice.Testing.Tokens.TestTokenV2.Allocation:TokenAllocationV1@93c942ae2b4c2ba674fb152fe38473c507bda4e82b4e4c5da55a552a9d8cce1d:Splice.Api.Token.AllocationV1:Allocation.allocation_executeTransferImpl: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/AccountConfig.daml:602` | Splice.Testing.Tokens.TestTokenV2.AccountConfig:extractAccountConfigMap: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/AccountConfig.daml:604` | Splice.Testing.Tokens.TestTokenV2.AccountConfig:extractAccountConfigMap: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:234` | Splice.Testing.Tokens.TestTokenV2.Allocation:applyAllocationTransitions: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:402` | Splice.Testing.Tokens.TestTokenV2.Allocation:debitInputTokens: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Transfer.daml:234` | Splice.Testing.Tokens.TestTokenV2.Transfer:applyTransferInstructionTransitions: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Transfer.daml:292` | Splice.Testing.Tokens.TestTokenV2.Transfer:createLockedInputs: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Transfer.daml:260` | Splice.Testing.Tokens.TestTokenV2.Transfer:sumAndArchiveHoldings: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2.daml:204` | Splice.Testing.Tokens.TestTokenV2:token_allocationFactoryV2_allocateImpl: unsafe primitive `coerceContractId` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Testing/Tokens/TestTokenV2/AccountConfig.daml:117` | Splice.Testing.Tokens.TestTokenV2.AccountConfig:AccountConfig.AuthorizeAllocationAction: interface contract id from argument `allocationCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Testing/Tokens/TestTokenV2/AccountConfig.daml:140` | Splice.Testing.Tokens.TestTokenV2.AccountConfig:AccountConfig.AuthorizeAllocationInstructionAction: interface contract id from argument `instrCid` |
| High | Medium | `untrusted-interface-exercise` | `Splice/Testing/Tokens/TestTokenV2/AccountConfig.daml:95` | Splice.Testing.Tokens.TestTokenV2.AccountConfig:AccountConfig.AuthorizeTransferInstructionAction: interface contract id from argument `instrCid` |
| Low | Medium | `missing-amount-check` | `Splice/Testing/Tokens/TestTokenV2/Transfer.daml:29` | Splice.Testing.Tokens.TestTokenV2.Transfer:TokenTransferOffer: ensure does not check `mintAmount` |
| Low | Medium | `time-dependence` | `Splice/Testing/Tokens/TestTokenV2.daml:115` | Splice.Testing.Tokens.TestTokenV2:TokenRules.TokenRules_OfferMint: ledger time decides a branch |
| Informational | Medium | `unused-template-field` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:156` | Splice.Testing.Tokens.TestTokenV2.Allocation:TokenAllocationV2: no code reads `availableActions` |
