# 02 — Test Case Design

The test case specifications and the matrix that ties every business rule to the cases that
exercise it.

## Contents

| File | Description |
|---|---|
| [`Test_Cases.csv`](Test_Cases.csv) | 95 test case specifications. Open in Excel, Google Sheets or any CSV viewer |
| [`Traceability_Matrix.md`](Traceability_Matrix.md) | Maps each rule ID (R1.1–R9.3) to its test case IDs, grouped by module |

## Test case columns

`TC_ID`, `Module`, `Rule_IDs`, `Title`, `Type`, `Priority`, `Preconditions`, `Steps`,
`Test_Data`, `Expected_Result`, `Automated`.

IDs follow `TC-M<module>-<nnn>`. For example, `TC-M4-007` is the seventh case in the coupons
and pricing module.

## By the numbers

| Cut | Breakdown |
|---|---|
| Total | 95 cases covering all 42 business rules |
| Automation | 86 automated (`Y`), 9 manual/exploratory (`N`) |
| Priority | Critical 7, High 49, Medium 35, Low 4 |
| Type | Positive 44, Negative 26, Negative/Boundary 19, Boundary 3, Positive/Boundary 2, Positive/Negative 1 |

## Modules

| Module | Area | Rules |
|---|---|---|
| M1 | Registration and login | R1.x |
| M2 | Catalog | R2.x |
| M3 | Cart | R3.x |
| M4 | Coupons and pricing | R4.x |
| M5 | Checkout | R5.x |
| M6 | Order lifecycle | R6.x |
| M7 | Reviews | R7.x |
| M8 | Admin | R8.x |
| M9 | Wishlist, banners, offers | R9.x |

## Techniques used

- **Boundary value analysis**: password length 7/8/20/21, quantity 0/1/10/11, the 5th failed
  login, the 6th order into a full delivery slot.
- **Equivalence partitioning**: valid and invalid email formats, serviceable and
  non-serviceable pincodes.
- **Negative and role cases**: every documented error response, plus 401 vs 403 checks.

## Maintaining it

The traceability matrix is generated from the CSV. If you add or change a case, regenerate the
matrix instead of editing it by hand.

## Related

- Source of the rules: [`../00_Application/docs/REQUIREMENTS.md`](../00_Application/docs/REQUIREMENTS.md)
- Automated implementation: [`../05_Test_Automation/`](../05_Test_Automation/)
- Results: [`../03_Test_Execution/Execution_Log.md`](../03_Test_Execution/Execution_Log.md)
