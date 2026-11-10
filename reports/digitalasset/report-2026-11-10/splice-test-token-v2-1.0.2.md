# splice-test-token-v2-1.0.2

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-test-token-v2 1.0.2 (LF 2.3)
- **SDK:** 3.5.2
- **Findings:** 13

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/AccountConfig.daml:592` | Splice.Testing.Tokens.TestTokenV2.AccountConfig:extractAccountConfigMap: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/AccountConfig.daml:592` | Splice.Testing.Tokens.TestTokenV2.AccountConfig:extractAccountConfigMap: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:219` | Splice.Testing.Tokens.TestTokenV2.Allocation:applyAllocationTransitions: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:398` | Splice.Testing.Tokens.TestTokenV2.Allocation:debitInputTokens: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Transfer.daml:221` | Splice.Testing.Tokens.TestTokenV2.Transfer:applyTransferInstructionTransitions: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Transfer.daml:282` | Splice.Testing.Tokens.TestTokenV2.Transfer:createLockedInputs: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Transfer.daml:257` | Splice.Testing.Tokens.TestTokenV2.Transfer:sumAndArchiveHoldings: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2.daml:197` | Splice.Testing.Tokens.TestTokenV2:token_allocationFactoryV2_allocateImpl: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:598` | eb77df925c1a27cc4bbbcf0972ea15fdf8b0f4f022319e36f18d5605f9de4ff9:Splice.Testing.Tokens.TestTokenV2.Allocation:TokenAllocationV1@93c942ae2b4c2ba674fb152fe38473c507bda4e82b4e4c5da55a552a9d8cce1d:Splice.Api.Token.AllocationV1:Allocation.allocation_executeTransferImpl: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:598` | eb77df925c1a27cc4bbbcf0972ea15fdf8b0f4f022319e36f18d5605f9de4ff9:Splice.Testing.Tokens.TestTokenV2.Allocation:TokenAllocationV1@93c942ae2b4c2ba674fb152fe38473c507bda4e82b4e4c5da55a552a9d8cce1d:Splice.Api.Token.AllocationV1:Allocation.allocation_executeTransferImpl: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:598` | eb77df925c1a27cc4bbbcf0972ea15fdf8b0f4f022319e36f18d5605f9de4ff9:Splice.Testing.Tokens.TestTokenV2.Allocation:TokenAllocationV1@93c942ae2b4c2ba674fb152fe38473c507bda4e82b4e4c5da55a552a9d8cce1d:Splice.Api.Token.AllocationV1:Allocation.allocation_executeTransferImpl: unsafe primitive `coerceContractId` |
| Low | Medium | `missing-amount-check` | `Splice/Testing/Tokens/TestTokenV2/Transfer.daml:29` | Splice.Testing.Tokens.TestTokenV2.Transfer:TokenTransferOffer: ensure does not check `mintAmount` |
| Informational | Medium | `unused-template-field` | `Splice/Testing/Tokens/TestTokenV2/Allocation.daml:156` | Splice.Testing.Tokens.TestTokenV2.Allocation:TokenAllocationV2: no code reads `availableActions` |
