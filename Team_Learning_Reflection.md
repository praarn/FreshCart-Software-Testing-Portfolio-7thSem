# Team Contribution and Learning Reflection

Fill in the `TODO` fields yourselves. Nothing here is written on a member's behalf.

## Team

| Member | Roll number | Role | GitHub username |
|---|---|---|---|
| Prapti R. N. | 1MS23IS094 | Test Analyst | [@praarn](https://github.com/praarn) |
| Poorvika G. J. | 1MS23IS090 | Test Engineer | [@poorvikagj](https://github.com/poorvikagj) |

## GitHub activity (from `git shortlog -sne HEAD`)

| Author in the history | GitHub | Commits |
|---|---|---|
| praarn | [@praarn](https://github.com/praarn) | 22 of 42 |
| poorvikagj | [@poorvikagj](https://github.com/poorvikagj) | 20 of 42 |

The repository has no pull requests or reviews yet. The assignment asks for commits, pull requests and reviews
from all three members, so the remaining open items below are best done in branches with reviewed pull requests.

## Deliverables by suggested role

The deliverables are listed under the role they naturally belong to. Confirm or change the assignment; the
`Author` column in `git log` is the record that counts.

| Role | Deliverables |
|---|---|
| Test Analyst | `Test_Plan/` (plan, requirements analysis), `Test_Case_Design/` (EP, BVA, decision table, state transition, test cases, xlsx, traceability) |
| Test Engineer | `Test_Execution/`, `Defect_Reports/`, `Test_Reports/`, `White_Box_Testing/`, `Black_Box_Testing/` and `Application/backend/tests/unit/` |
| Automation and QA Engineer | `Test_Automation/`, `API_Testing/`, `.github/workflows/ci.yml`, `Screenshots/` |

## Open items per role (to create real, attributable contributions)

| Role | Item |
|---|---|
| Test Analyst | Review the Test Plan and the new black-box case rows (`Black-box EP` / `Black-box BVA` in `Test_Cases.csv`); the four formerly unmapped EP classes are now covered by TC-M1-029, TC-M1-030 and TC-M5-019 |
| Test Engineer | Run `mutmut` on `pricing_service.py` and write `White_Box_Testing/Mutation_Testing.md`; decide whether to remove the redundant branch found in `complete_delivery` |
| Automation and QA Engineer | Watch the first CI run on GitHub, confirm the Selenium job is stable on the runner, add the green-run screenshot to `Screenshots/` |

## Individual contribution and reflection

### Prapti R. N. (Test Analyst)

- Contributions (from `git log --author`): TODO
- What I learned: TODO (write in your own words)
- What was difficult: TODO (write in your own words)
- What I would do differently: TODO (write in your own words)

### Poorvika G. J. (Test Engineer)

- Contributions (from `git log --author`): TODO
- What I learned: TODO (write in your own words)
- What was difficult: TODO (write in your own words)
- What I would do differently: TODO (write in your own words)

## Team reflection

TODO (write in your own words)

Prompts: Which technique found the most defects? Which defect was hardest to isolate and why? What would you
automate earlier next time?
