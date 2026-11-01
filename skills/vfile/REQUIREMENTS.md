## skills/vfile/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| F1 | Invoked as `/vfile bug\|refactor\|feature [<one line>]`. It replaces `tdd-fix` and `tdd-candidates`. | One filer. |
| F2 | For a bug, it asks only for what the line left out among: happened, expected, steps, environment. | |
| F3 | A refactor's acceptance criteria are structural predicates. | |
| F4 | `## Blocked by` holds only blocker lines or `None.`. | Every `#N` in that section blocks. |
| F5 | `Test command:` appears once, on the last line. | |
| F6 | A sweep (the same fix at N sites) has one covering criterion plus its guard's go-red criterion, and the sites are listed under Problem. | #1037: per-site criteria took 17 steps to deliver one change. |
| F7 | It adds the opt-in label only when the human said to take the issue. | The label alone opts an issue in. |
| F8 | Before filing, it searches for duplicates and related issues, and names any follow-ups. | "why did you not include that in the initial filing". |
| F9 | It checks that every input a criterion names exists, and that the criterion's literal rule meets its goal. | Three coordinator-written criteria missed their goal. |
| F10 | It reports the url and whether the issue is now solvable. | |
| F11 | Near its top, the skill says it obeys `operator/PRINCIPLES.md` and reads it first. | PR #2061 (vgroom) passed its rows without it, so no principle reached the skill. |
| F12 | Every subagent brief the skill writes (the F8 duplicate search, the F9 input check) asks for a return of at most 10 lines (P6), and says that all writes stay in the project repo and that a fix belonging elsewhere is reported, not made (P11, in its words). | PR #2061 (vgroom) wrote an unbounded brief with no repo boundary. |
| F13 | For a feature, it asks only for what the line left out among: the problem, the behaviour wanted and what done looks like, and each acceptance criterion is one behaviour, pinned by a case. | `/vplan` needs a filer for its children. |
| F14 | An issue changing graded prose carries `## Requirements`, with each unit under a `### <path>` heading (`### <path> (new)` only for a file that does not exist yet; a `##` heading is not read), each ID cell the bare ID, and an amended row its full new text; the skill shows a literal example heading. | `skill-edit-step.sh` and `run-conductor.sh` refuse anything else (exit 2), and #2502, #2524, #2841 and #2828 were refused this way. |
| F15 | A sweep's sites that group into changes useful on their own are filed as one sweep per group, whatever the extra runs cost. | F6 bounds criteria, and must not read as a reason to batch (P16). |
