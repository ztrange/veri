Seen in #1468's resume (PR #1566), 2026-10-15.

## Problem

After a first NOT OK, the coordinator amends an issue by appending criteria to ## Acceptance criteria, and the run is resumed once. The resumed conductor plans the new criteria's steps with `add-ledger-step.sh`, so each one is marked `⟦added⟧` and counts against `VERI_STEP_GROWTH`, which defaults to 5 and bounds plan growth the run *discovers* (ADR-0022). Amended criteria are not discovered growth. They are scope a human added, and they routinely need more than 5 steps: #1468's four amended criteria took 16.

The budget is in the wrong place, so the conductor improvised. It wrote `VERI_STEP_GROWTH=18` into its own scratch helper (`.tdd/c.sh`), raised it to 24 later in the run, and gave its reason in prose. Nothing in `SKILL.md` lets a conductor change a budget mid-run. The budget axes exist so that kind of decision is never made by the thing being budgeted. Under the documented behaviour, the run would have filed the extra steps under `## Owed steps` or bailed `step-too-big`, and the amended criteria would have gone unbuilt.

## Decision (Mario, 2026-10-15: option a)

How a resume after an amendment should be bounded:

- (a) **Recommended.** Steps planned for criteria that are unticked when the resume starts and that no ledger step yet serves are *planned* steps (the resume's own scoping, as at a fresh start), not `⟦added⟧`. They do not count against `VERI_STEP_GROWTH`. Discovered growth during the resume still counts.
- (b) Keep counting them, and have the launcher set `VERI_STEP_GROWTH` explicitly at resume time.

Either way, the conductor must never change a budget itself.

## Acceptance criteria

- [x] On a resume whose issue carries an unticked criterion that no ledger step's `⟦criterion k⟧` serves, the steps planned for it are inserted without `⟦added⟧` and do not count toward `VERI_STEP_GROWTH`. A step added later in the same resume for a criterion that already had steps still counts. Pinned by a case for each.
- [x] `SKILL.md` states that a conductor never sets or raises `VERI_STEP_GROWTH`, `REVISE_BUDGET`, `VERI_REFACTOR_BUDGET`, `VERI_STUCK_RETRIES` or `VERI_NO_VERDICT_RETRIES` mid-run, and that a budget it cannot fit inside is a bail. A prose case pins the sentence.
- [ ] `add-ledger-step.sh --planned --criterion <k>` refuses with exit 2, naming k, when k is not a criterion of the issue that is unticked in the issue body the run read (a number the issue does not have, or a ticked criterion). Nothing is inserted and nothing is filed as owed. A k that is unticked and that no step serves is still accepted. Pinned by a case each: an unknown k, a ticked k, and an accepted k.
- [ ] Every description of `add-ledger-step.sh` and of the resume agrees with the `--planned` behaviour: the usage text (`add_ledger_step.py`), the shim's header (`add-ledger-step.sh`, including its exit-2 list), `SKILL.md`'s scripts-list entry, and Resume sub-step 1, which says "Do not re-plan" while sub-step 3 now plans the amended criteria. Pinned by a prose case per place.

## Blocked by

- #1568: both edit `skills/tdd/SKILL.md` (one SKILL.md editor at a time)

Test command: make test

