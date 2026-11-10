# splice-api-reward-assignment-v1-1.0.0

[Back to the summary](../report-2026-11-10.md)

- **Package:** splice-api-reward-assignment-v1 1.0.0 (LF 2.1)
- **SDK:** 3.4.11
- **Findings:** 1

| Impact | Confidence | Detector | Location | Finding |
|---|---|---|---|---|
| Medium | Medium | `over-disclosure` | `Splice/Api/RewardAssignmentV1.daml:46` | Splice.Api.RewardAssignmentV1:RewardCoupon.RewardCoupon_AssignBeneficiaries: choice observers taken from argument `newBeneficiaries` |
