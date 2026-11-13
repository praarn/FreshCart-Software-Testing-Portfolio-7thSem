# Team Contribution and Learning Reflection

Fill in the `TODO` fields yourselves. Nothing here is written on a member's behalf.

## Team

| Member | Roll number | Role | GitHub username |
|---|---|---|---|
| TODO: name | TODO | Test Analyst | TODO |
| TODO: name | TODO | Test Engineer | TODO |
| TODO: name | TODO | Automation and QA Engineer | TODO |

## GitHub activity (from `git shortlog -sne HEAD`, generated 2026-11-14)

| Author in the history | Commits |
|---|---|
| one identity (`praarn`) | 26 of 26 |

All commits so far come from a single identity, and the repository has no pull requests or reviews. The
assignment asks for commits, pull requests and reviews from all three members. This cannot be fixed by editing
history. Each member needs to make real changes from their own account, for example the follow-ups listed
under "Open items per role" below, each in a branch with a pull request reviewed by another member.

## Deliverables by suggested role

The deliverables are listed under the role they naturally belong to. Confirm or change the assignment; the
`Author` column in `git log` is the record that counts.

| Role | Deliverables |
|---|---|
| Test Analyst | `01_Test_Plan/` (plan, requirements analysis), `02_Test_Case_Design/` (EP, BVA, decision table, state transition, test cases, xlsx, traceability) |
| Test Engineer | `03_Test_Execution/`, `04_Defect_Reports/`, `06_Test_Reports/`, `08_White_Box_Testing/` and `00_Application/backend/tests/unit/` |
| Automation and QA Engineer | `05_Test_Automation/`, `09_API_Testing/`, `.github/workflows/ci.yml`, `07_Screenshots/` |

## Open items per role (to create real, attributable contributions)

| Role | Item |
|---|---|
| Test Analyst | Add EP cases for the 4 unmapped classes in `Equivalence_Partitioning.md` (password without a letter, non-digit phone, pincode below range, wrong-length pincode); review the Test Plan |
| Test Engineer | Run `mutmut` on `pricing_service.py` and write `08_White_Box_Testing/Mutation_Testing.md`; decide whether to remove the redundant branch found in `complete_delivery` |
| Automation and QA Engineer | Watch the first CI run on GitHub, confirm the Selenium job is stable on the runner, add the green-run screenshot to `07_Screenshots/` |

## Individual contribution and reflection

### Member 1: TODO name (Test Analyst)

- Contributions (from `git log --author`): TODO
- What I learned: TODO (write in your own words)
- What was difficult: TODO (write in your own words)
- What I would do differently: TODO (write in your own words)

### Member 2: TODO name (Test Engineer)

- Contributions (from `git log --author`): TODO
- What I learned: TODO (write in your own words)
- What was difficult: TODO (write in your own words)
- What I would do differently: TODO (write in your own words)

### Member 3: TODO name (Automation and QA Engineer)

- Contributions (from `git log --author`): TODO
- What I learned: TODO (write in your own words)
- What was difficult: TODO (write in your own words)
- What I would do differently: TODO (write in your own words)

## Team reflection

TODO (write in your own words)

Prompts: Which technique found the most defects? Which defect was hardest to isolate and why? What would you
automate earlier next time?
