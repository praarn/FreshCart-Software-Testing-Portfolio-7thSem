# 02 — Test Case Design

The test case specifications and the matrix that ties every business rule to the cases that
exercise it.

## Contents

| File | Description |
|---|---|
| [`Test_Cases.csv`](Test_Cases.csv) | Test case specifications (source of truth) |
| [`Functional_Test_Cases.xlsx`](Functional_Test_Cases.xlsx) | The same cases as a formatted workbook (frozen header, filters) plus a Summary sheet |
| [`Traceability_Matrix.md`](Traceability_Matrix.md) | Each rule ID (R1.1-R9.3) mapped to its test case IDs |
| [`Equivalence_Partitioning.md`](Equivalence_Partitioning.md) | Valid/invalid classes for name, email, password, phone, pincode, payment |
| [`Boundary_Value_Analysis.md`](Boundary_Value_Analysis.md) | Boundaries for 18 numeric/length rules |
| [`Decision_Table.md`](Decision_Table.md) | Coupon eligibility and payment validity |
| [`State_Transition.md`](State_Transition.md) | Order lifecycle and account lockout state machines |
| `generate_artifacts.py` | Regenerates the matrix and the workbook from the CSV |

## Test case columns

`TC_ID`, `Module`, `Rule_IDs`, `Title`, `Type`, `Priority`, `Preconditions`, `Steps`,
`Test_Data`, `Expected_Result`, `Automated`.

IDs follow `TC-M<module>-<nnn>`. For example, `TC-M4-007` is the seventh case in the coupons
and pricing module.

## By the numbers

Counts come from `python generate_artifacts.py` and the `Summary` sheet of the workbook.

| Cut | Meaning |
|---|---|
| `Automated = Y` | Selenium test in `05_Test_Automation` |
| `Automated = A` | API request in `09_API_Testing` (Newman) |
| `Automated = B` | Black-box technique case (equivalence partitioning or boundary value analysis), parametrized pytest in `11_Black_Box_Testing` |
| `Automated = U` | Unit test in `00_Application/backend/tests/unit` (includes the white-box basis path and coverage cases) |
| `Automated = N` | Manual or scripted by hand; result in `03_Test_Execution` |

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

Two black-box methods (executed in [`../11_Black_Box_Testing/`](../11_Black_Box_Testing/README.md)) and two white-box
methods (executed in [`../08_White_Box_Testing/`](../08_White_Box_Testing/README.md)):

| Kind | Technique | Document | Cases |
|---|---|---|---|
| Black box 1 | Equivalence partitioning | `Equivalence_Partitioning.md` | 29 classes designed, all mapped; 19 `B` cases (type `Black-box EP`) run every class |
| Black box 2 | Boundary value analysis | `Boundary_Value_Analysis.md` | min-1/min/max/max+1 for 18 rules designed; 26 `B` cases (type `Black-box BVA`) probe every limit |
| White box 1 | Basis path testing | `../08_White_Box_Testing/Basis_Path_Testing.md` | 3 functions: `TC-M4-022`, `TC-M5-028`, `TC-M6-020` (type `White-box basis path`) |
| White box 2 | Statement, branch and condition coverage | `../08_White_Box_Testing/Coverage_Report.md` | `TC-M4-023`, `TC-M5-029`, `TC-M6-021`, `TC-M1-038`, `TC-M1-039` (type `White-box coverage`) |
| Supporting | Decision table | `Decision_Table.md` | 7 coupon rules, 8 payment rules |
| Supporting | State transition | `State_Transition.md` | 7 valid + 8 invalid order transitions, 5 lockout transitions |
| Supporting | Negative and role cases | this CSV | every documented error response, 401 vs 403 |

## Maintaining it

The matrix and workbook are generated from the CSV. After adding or changing a case run
`python generate_artifacts.py` instead of editing them by hand.

## Related

- Source of the rules: [`../00_Application/docs/REQUIREMENTS.md`](../00_Application/docs/REQUIREMENTS.md)
- Automated implementation: [`../05_Test_Automation/`](../05_Test_Automation/)
- Results: [`../03_Test_Execution/Execution_Log.md`](../03_Test_Execution/Execution_Log.md)
