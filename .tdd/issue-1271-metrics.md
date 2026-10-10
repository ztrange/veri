### 📊 Metrics — issue 1271

Wall time for the issue: 3653 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1393.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 1 | 2 | 998 | 12489 | 34312 | 0.15 |
| red | 4 | 0 | 0 | 0 | 447 | 166 | 52 | 100 | 22253 | 3043894 | 231200 | 1.45 |
| pin | 4 | 3 | 1 | 0 | 406 | 88 | 30 | 60 | 10936 | 1500723 | 197072 | 1.05 |
| green | 8 | 3 | 1 | 0 | 604 | 155 | 55 | 108 | 18532 | 2584130 | 358269 | 1.88 |
| refactor | 6 | 3 | 0 | 0 | 226 | 57 | 24 | 48 | 6716 | 1012618 | 251528 | 1.17 |
| diff | 4 | 2 | 0 | 0 | 500 | 77 | 28 | 54 | 9594 | 1316533 | 183317 | 0.96 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 12 | 2 | 0 | 1074 | 226 | 74 | 148 | 27758 | 3393786 | 616468 | 3.08 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 1119 | 324 | 116 | 224 | 41271 | 6076601 | 639230 | 3.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 244 | 0.58 | 0 | 0.00 |
| green | 205 | 0.95 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary refuses a bad tunable with exit 2 and no conductor launched — VERI_PARALLEL of 0, a word or set-but-empty; VERI_MAX_ISSUES of a word, 0, a negative, a fraction or set-but-empty, naming it and the value; VERI_CONDUCTOR_CTX_BUDGET of a word, a fraction or a negative, naming it: replaces 'VERI_PARALLEL not a whole number >= 1 (0, a word, set-but-empty) is exit 2 with no conductor launched', '#505 VERI_MAX_ISSUES not a whole number >= 1 (a word, 0, a negative, a fraction) is exit 2 naming it and the value, with no conductor launched', '#505 VERI_MAX_ISSUES set but empty is exit 2 naming it and the empty value '', with no conductor launched', 'VERI_CONDUCTOR_CTX_BUDGET not a whole number (a word, a fraction, a negative) is exit 2 naming it, with no conductor launched' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 135 | 45 | 90 | 16419 | 2280668 | 280792 | 1.52 | 757 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary and a faked solvable-issues queue schedules launches: VERI_PARALLEL unset runs them one after another; launches follow the queue's printed order and never an issue it did not print; a finished issue still solvable is not relaunched; an issue that became solvable meanwhile is launched next; VERI_MAX_ISSUES caps the launches and unset caps nothing; with VERI_PARALLEL=1 it exits 0 once nothing is left and when every solvable issue is parked: replaces 'VERI_PARALLEL unset runs two solvable issues' conductors one after another', 'with VERI_PARALLEL=1 the launcher exits 0 once nothing is left to take after launching conductors, and exits 0 when every issue still solvable is parked', 'launches follow solvable-issues.sh's printed order and never an issue it did not print', 'an issue still solvable after its conductor finished is not launched a second time', 'an issue that became solvable while another conductor ran is launched next', 'VERI_MAX_ISSUES caps the launches of one invocation', '#505 VERI_MAX_ISSUES unset applies no cap and launches every solvable issue' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 249 | 81 | 158 | 31404 | 4280047 | 497552 | 2.73 | 889 | red 1/2, green 1/2 | 1/5 | structural-owed |  |  | already-satisfied |
| parallel-conductors.sh driven through run_cli with VERI_PARALLEL=2 starts two solvable issues' conductors before either ends: replaces 'VERI_PARALLEL=2 runs two solvable issues' conductors at once — both start before either ends' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 82 | 35 | 68 | 10614 | 1580650 | 259725 | 1.30 | 336 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| make hermetic's slice of parallel-conductors.test.sh in tests/hermetic/hermetic-suites.test.sh still matches the suite after the removals — its markers and its assertion count updated or the slice dropped — so the slice's own check does not report that the markers moved ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 15 | 30 | 5309 | 735286 | 88087 | 0.48 | 283 | n/a | n/a | n/a |  |  | full |
| parallel-conductors.test.sh's remaining cases still pass; if none remain the file is gone, no guard table, roster, workflow comment or CLAUDE.md count outside .tdd/ and docs/ names it, and CLAUDE.md's suite count matches the tree ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 13 | 24 | 4285 | 581247 | 95230 | 0.48 | 266 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary refuses a bad tunable with exit 2 and no conductor launched — VERI_PARALLEL of 0, a word or set-but-empty; VERI_MAX_ISSUES of a word, 0, a negative, a fraction or set-but-empty, naming it and the value; VERI_CONDUCTOR_CTX_BUDGET of a word, a fraction or a negative, naming it: replaces 'VERI_PARALLEL not a whole number >= 1 (0, a word, set-but-empty) is exit 2 with no conductor launched', '#505 VERI_MAX_ISSUES not a whole number >= 1 (a word, 0, a negative, a fraction) is exit 2 naming it and the value, with no conductor launched', '#505 VERI_MAX_ISSUES set but empty is exit 2 naming it and the empty value '', with no conductor launched', 'VERI_CONDUCTOR_CTX_BUDGET not a whole number (a word, a fraction, a negative) is exit 2 naming it, with no conductor launched' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 79 | 0.38 |
| parallel-conductors.sh driven through run_cli with conductors faked at the Popen boundary and a faked solvable-issues queue schedules launches: VERI_PARALLEL unset runs them one after another; launches follow the queue's printed order and never an issue it did not print; a finished issue still solvable is not relaunched; an issue that became solvable meanwhile is launched next; VERI_MAX_ISSUES caps the launches and unset caps nothing; with VERI_PARALLEL=1 it exits 0 once nothing is left and when every solvable issue is parked: replaces 'VERI_PARALLEL unset runs two solvable issues' conductors one after another', 'with VERI_PARALLEL=1 the launcher exits 0 once nothing is left to take after launching conductors, and exits 0 when every issue still solvable is parked', 'launches follow solvable-issues.sh's printed order and never an issue it did not print', 'an issue still solvable after its conductor finished is not launched a second time', 'an issue that became solvable while another conductor ran is launched next', 'VERI_MAX_ISSUES caps the launches of one invocation', '#505 VERI_MAX_ISSUES unset applies no cap and launches every solvable issue' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | structural-owed | PASS | 0 | 77 | 0.44 |
| parallel-conductors.sh driven through run_cli with VERI_PARALLEL=2 starts two solvable issues' conductors before either ends: replaces 'VERI_PARALLEL=2 runs two solvable issues' conductors at once — both start before either ends' in skills/tdd/scripts/tests/parallel-conductors.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 70 | 0.36 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 40 | 38 | 34 | 1 | 1 | 0 | 27 | 26 | 21 | 1 | 0 | 26 | 25 | 25 | 45 | 68 |  |  |  |  |
| target | 0 | 126 | 1 | 1 | 0 | 125 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 23 | 1 | 1 | 0 | 0 |
| fast | 28 | 28 | 25 | 23 | 23 | 22 | 21 | 24 | 22 | 23 | 24 | 24 | 22 | 23 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 190 | 372 | 69029 | 9470387 | 1255698 | 6.66 |
