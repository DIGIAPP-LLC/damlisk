# splice-token-standard-utils-2.0.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-token-standard-utils 2.0.0 (LF 2.1)
- **SDK:** 3.5.2
- **Findings:** 9

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| High | High | `unsafe-primitive` | `Splice/TokenStandard/Utils/Internal/Allocations.daml:600` | Splice.TokenStandard.Utils.Internal.Allocations:allocationFactoryV1_allocateDefaultImplUsingV2: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/TokenStandard/Utils/Internal/Allocations.daml:603` | Splice.TokenStandard.Utils.Internal.Allocations:allocationFactoryV1_allocateDefaultImplUsingV2: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/TokenStandard/Utils/Internal/Allocations.daml:610` | Splice.TokenStandard.Utils.Internal.Allocations:allocationFactoryV1_allocateDefaultImplUsingV2: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/TokenStandard/Utils/Internal/Allocations.daml:1047` | Splice.TokenStandard.Utils.Internal.Allocations:allocationFactoryV1_allocateDefaultImplUsingV2: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/TokenStandard/Utils/Internal/Allocations.daml:1051` | Splice.TokenStandard.Utils.Internal.Allocations:allocationFactoryV1_allocateDefaultImplUsingV2: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/TokenStandard/Utils/Internal/Allocations.daml:656` | Splice.TokenStandard.Utils.Internal.Allocations:tryDowncast_v2_v1_AllocationInstructionView: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/TokenStandard/Utils/Internal/Conversions.daml:104` | Splice.TokenStandard.Utils.Internal.Conversions:fromAnyContractId: unsafe primitive `coerceContractId` |
| High | High | `unsafe-primitive` | `Splice/TokenStandard/Utils/Internal/Conversions.daml:107` | Splice.TokenStandard.Utils.Internal.Conversions:toAnyContractId: unsafe primitive `coerceContractId` |
| Medium | High | `hardcoded-party` | `Splice/TokenStandard/Utils/Internal/Conversions.daml:138` | Splice.TokenStandard.Utils.Internal.Conversions:specialAccountOwnerStubV1: party built from text literal "cip-112_no-owner::122000..." |
