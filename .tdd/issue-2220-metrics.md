### 📊 Metrics — issue 2220

Wall time for the issue: 3431 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2225.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.06 over 50 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88627 |
| 2 | $0.02 | 89042 |
| 3 | $0.02 | 89825 |
| 4 | $0.03 | 91765 |
| 5 | $0.02 | 92051 |
| 6 | $0.02 | 92408 |
| 7 | $0.02 | 92733 |
| 8 | $0.02 | 93052 |
| 9 | $0.02 | 93664 |
| 10 | $0.03 | 94665 |
| 11 | $0.05 | 98144 |
| 12 | $0.04 | 100770 |
| 13 | $0.04 | 103686 |
| 14 | $0.04 | 106070 |
| 15 | $0.02 | 106363 |
| 16 | $0.03 | 106965 |
| 17 | $0.03 | 107527 |
| 18 | $0.03 | 108063 |
| 19 | $0.03 | 108743 |
| 20 | $0.03 | 110099 |
| 21 | $0.03 | 111197 |
| 22 | $0.03 | 112030 |
| 23 | $0.03 | 112924 |
| 24 | $0.03 | 113463 |
| 25 | $0.03 | 114111 |
| 26 | $0.03 | 115034 |
| 27 | $0.04 | 117466 |
| 28 | $0.03 | 118139 |
| 29 | $0.03 | 118468 |
| 30 | $0.03 | 119380 |
| 31 | $0.03 | 120519 |
| 32 | $0.03 | 121183 |
| 33 | $0.03 | 122126 |
| 34 | $0.04 | 123460 |
| 35 | $0.03 | 124206 |
| 36 | $0.03 | 125108 |
| 37 | $0.03 | 126153 |
| 38 | $0.03 | 126856 |
| 39 | $0.03 | 127795 |
| 40 | $0.04 | 129138 |
| 41 | $0.03 | 129991 |
| 42 | $0.03 | 130582 |
| 43 | $0.03 | 131341 |
| 44 | $0.03 | 131693 |
| 45 | $0.03 | 131942 |
| 46 | $0.03 | 132296 |
| 47 | $0.03 | 132803 |
| 48 | $0.03 | 133058 |
| 49 | $0.03 | 133379 |
| 50 | $0.03 | 133812 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 14 | 1 | 2 | 1357 | 0 | 31005 | 0.09 |
| diff | 6 | 3 | 0 | 0 | 612 | 194 | 37 | 70 | 13759 | 1104114 | 137481 | 0.59 |
| red | 3 | 0 | 0 | 0 | 247 | 123 | 23 | 42 | 10939 | 687758 | 66233 | 0.34 |
| pin | 3 | 3 | 0 | 0 | 170 | 69 | 14 | 28 | 5012 | 381533 | 45703 | 0.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 381 | 124 | 24 | 48 | 9444 | 586165 | 132531 | 0.48 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 668 | 276 | 51 | 94 | 21623 | 1587240 | 147891 | 0.74 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The Refactor-loop reader guard in skills/tdd/scripts/tests/py/unit/test_skill_refactor_readers.py does its sweep in a module-level function that takes the index entries and the allow-list and returns the stray case ids, the guard case calling it; the sweep is made cheap (test-only, no production change), so the guard case still passes on the current tree and runs within the unit tier's ~100 ms budget, or, if it cannot, the guard case moves out of tests/py/unit/ into tests/py/ keeping its tree_audit mark naming what it sweeps ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 100 | 20 | 38 | 8165 | 670578 | 79635 | 0.35 | 411 | n/a | n/a | n/a |  |  | full |
| The Refactor-loop reader guard's sweep function flags a case that reads SKILL.md's Refactor loop subsection by content and is missing from the allow-list, and flags nothing once that case is on it: a small unmarked case (no git, no process, no tree sweep) beside the guard, driving the sweep function on one synthetic test module written under tmp_path, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 71 | 14 | 26 | 6191 | 405071 | 38741 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| The phases-step reader guard in skills/tdd/scripts/tests/py/unit/test_skill_phased_readers.py does its sweep in a module-level function that takes the index entries and the allow-list and returns the stray case ids, the guard case calling it; the sweep is made cheap (test-only, no production change), so the guard case still passes on the current tree and runs within the unit tier's ~100 ms budget, or, if it cannot, the guard case moves out of tests/py/unit/ into tests/py/ keeping its tree_audit mark naming what it sweeps ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 9 | 16 | 3383 | 223757 | 31812 | 0.14 | 215 | n/a | n/a | n/a |  |  | full |
| The phases-step reader guard's sweep function flags a case that reads SKILL.md's phases-step subsection by content and is missing from the allow-list, and flags nothing once that case is on it: a small unmarked case (no git, no process, no tree sweep) beside the guard, driving the sweep function on one synthetic test module written under tmp_path, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 12 | 22 | 4159 | 326980 | 35576 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| The Preflight reader guard in skills/tdd/scripts/tests/py/test_skill_preflight.py does its sweep in a module-level function that takes the index entries and the allow-list and returns the stray case ids, the guard case calling it; the sweep is made cheap (test-only, no production change), so the guard case still passes on the current tree, keeping its tree_audit mark naming what it sweeps ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 8 | 16 | 2211 | 209779 | 26034 | 0.11 | 234 | n/a | n/a | n/a |  |  | full |
| The Preflight reader guard's sweep function flags a case that reads SKILL.md's Preflight section by content and is missing from the allow-list, and flags nothing once that case is on it: a small unmarked case (no git, no process, no tree sweep) beside the guard, driving the sweep function on one synthetic test module written under tmp_path, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 66 | 11 | 22 | 5601 | 337240 | 37619 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 25 | 21 | 20 | 23 | 17 | 18 | 26 | 20 |  |  |  |  |
| affected | 27 | 27 | 23 | 12 | 2 | 22 | 25 | 22 | 19 | 23 | 26 | 17 |
| target | 11 | 11 | 11 | 2 | 12 | 2 | 9 | 11 | 10 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 75 | 142 | 31067 | 2173405 | 280422 | 1.23 |
