### 📊 Metrics — issue 930

Wall time for the issue: 7658 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 15 of 17 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/962.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 38 | 32 | 2 | 4 | 3413 | 77853 | 57864 | 0.55 |
| red | 11 | 1 | 0 | 0 | 960 | 770 | 137 | 252 | 74246 | 9681130 | 829555 | 10.06 |
| pin | 9 | 9 | 0 | 0 | 354 | 219 | 55 | 110 | 21321 | 3191738 | 527454 | 5.28 |
| green | 6 | 1 | 2 | 0 | 1114 | 507 | 86 | 166 | 48142 | 6333852 | 360935 | 5.12 |
| refactor | 2 | 1 | 0 | 0 | 297 | 107 | 23 | 44 | 8912 | 1528565 | 130282 | 1.53 |
| diff | 10 | 5 | 0 | 0 | 408 | 224 | 54 | 108 | 20750 | 3145225 | 593844 | 5.80 |
| rebase | 2 | 1 | 0 | 0 | 1741 | 52 | 12 | 24 | 3962 | 689615 | 116766 | 1.15 |
| predicate | 2 | 0 | 0 | 0 | 30 | 20 | 5 | 10 | 1441 | 212626 | 106082 | 0.92 |
| structural | 1 | 0 | 0 | 0 | 24 | 16 | 6 | 12 | 1651 | 336716 | 54692 | 0.54 |
| transform | 1 | 1 | 0 | 0 | 27 | 17 | 5 | 10 | 1628 | 267626 | 53936 | 0.52 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 22 | 20 | 2 | 0 | 2211 | 687 | 143 | 282 | 63397 | 8744954 | 1236239 | 12.91 |
| developer | claude-opus-5-5 | 23 | 0 | 0 | 0 | 2782 | 1277 | 242 | 458 | 122069 | 16719992 | 1595171 | 18.55 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 1990 | 8.75 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| rebase | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 30 | 0.92 |
| structural | 0 | 0.00 | 24 | 0.54 |
| transform | 0 | 0.00 | 27 | 0.52 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| metrics.sh run through a symlink to the skill directory, from another working directory, answers with the same stdout and exit code as run in place, reading the caller's working directory's .tdd/events.jsonl and .tdd/issue-<n>.md and never the skill's — a case in tests/metrics.test.sh, written against the bash script ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 106 | 19 | 36 | 9596 | 1172676 | 124769 | 1.42 | unknown | unknown | unknown | unknown |  |  | pin |
| metrics.sh run in a working directory with no .tdd/events.jsonl exits 1 and prints nothing on stdout — a case in tests/metrics.test.sh, written against the bash script ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 15 | 28 | 5355 | 849364 | 116834 | 1.21 | unknown | unknown | unknown | unknown |  |  | pin |
| the port: veri.metrics.main([]) and main([""]) return 2 with stderr exactly "usage: metrics.sh <issue-number>\n", nothing on stdout and no .tdd/ file read; main(["108"]) over a tmp_path working directory holding a one-step .tdd/events.jsonl returns 0 with stdout beginning "### 📊 Metrics — issue 108\n", and main(["108", "extra"]) prints the same stdout; main(["108"]) over a .tdd/issue-108.md mixing an indented "  - [X] …", a "-\t[ ] …", a "* [ ] …", a "- [y] …" and a "text - [ ] …" prints "Steps done: 1 of <n> planned." with <n> = len(veri.ledger.ledger_steps(text)), and "Steps done: 1 of unknown planned." for a ledger with no step line; and pytest cases pin every branch issue #930 lists under "Order matters (#797)" (missing log, non-JSON line and non-object line raising with nothing on stdout; unknown planned count for a directory ledger, NULs dropped, the splitlines over-count; a non-numeric secs leaving the earlier lines on stdout; done/bail/stop with missing keys printing unknown and a resume after a done staying landed; integer status 2 not a kill; the answered-models list split, deduplicated and sorted; the "?" revise budget, the empty-transforms refactor cells, the skipped test-run and unknown tier with padded rows, "Stopped: ?"; two main calls rendering independent reports) — the module carries the whole inline program, imports read_events and ledger_steps and starts no process, and metrics.sh becomes a /bin/sh shim over it in the same commit, its header keeping a lowercase "usage: metrics.sh <issue-number>" line and no issue number; that commit also cuts '#495 the planned-step count is the number of ledger-steps.sh's records, counting no box of its own' from skills/tdd/scripts/tests/metrics.test.sh: replaces 'migration slice 4 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh, metrics.sh leaving slice 4's list and its other scripts staying ⟦replaces-case⟧ ⟦criterion 1⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 688 | 122 | 234 | 62622 | 8590740 | 611373 | 7.86 | 1658 | 2/2 | 4/5 | structural-owed |  |  | full |
| the port step's commit cuts the #495 case at tests/metrics.test.sh:2919-2947 and adds the ledger-grammar pytest cases criterion 2 names, asserting through files under tmp_path only, patching no function of veri.metrics or veri.ledger ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 12 | 24 | 3977 | 705155 | 119896 | 1.18 | 118 | unknown | unknown | unknown |  |  | full |
| every branch issue #930 lists under "Order matters (#797)" is pinned by a pytest case in tests/py/test_metrics.py added in the port step's commit or an earlier one ⟦diff-checked⟧ ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 10 | 20 | 4992 | 566067 | 121806 | 1.19 | 89 | unknown | unknown | unknown |  |  | full |
| the port step's commit changes no assertion of tests/metrics.test.sh, tests/skill-event-marks.test.sh or tests/dashboard.test.sh — its diff to those suites touches only copy lines, stub libs and the cut #495 case ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 9 | 18 | 3307 | 478136 | 110986 | 1.05 | 116 | unknown | unknown | unknown |  |  | full |
| tests/py/test_metrics.py asserts in-process, through veri.metrics.main(argv) over tmp_path files, what the tests/metrics.test.sh contract cases at :236-931 assert (phase rows, per-step section, revise and refactor budgets, wall and API seconds, turns/tokens/dollars and the conductor-cost line, rework, waste) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 167 | 26 | 50 | 17046 | 2149340 | 167088 | 2.11 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_metrics.py asserts in-process what the contract cases at :934-1302 assert (steps done of planned, outcome naming a bail's classification or a landed PR, pin and step-done counting, bail then resume then done, the issue wall from the last resume or the first event, sums over both runs) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 87 | 16 | 30 | 8487 | 1015312 | 135566 | 1.46 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_metrics.py asserts in-process what the contract cases at :1305-1584 assert (no-verdict relaunch count, triage stopped values, #452 spent= column and at=over-budget versus at=exhausted, the per-tier test-run section, the stop Outcome line, a resume after a stop) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 77 | 18 | 34 | 7978 | 1200490 | 136457 | 1.49 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_metrics.py asserts in-process what the #486 and #643 clock cases at :1587-1875 assert (awake span excluding a gap, the not-running line never negative, step and phase walls off awake readings, the wall-clock fallback and its sentence) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 94 | 23 | 44 | 9194 | 1548683 | 133816 | 1.56 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_metrics.py asserts in-process what the #488 and #454 cases at :1878-2171 assert (per-phase revise cells, the By-step kind column, the note line naming turns, dollars and the three model knobs) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 94 | 19 | 36 | 9191 | 1240642 | 133629 | 1.50 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_metrics.py asserts in-process what the #502, #503, #585, #596 and #726 cases at :2296-2917 assert (per-pass refactor rows with verdict, wall, cost and revises; the Structural pass section, its stop reasons and inconsistent marks, and the unmarked pass) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 137 | 24 | 44 | 14104 | 1724916 | 155544 | 1.87 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_metrics.py asserts in-process what the #604 cases at :2949-3103 assert (the By model table, the Models requested line under VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER set through the environment, a model not recorded) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 99 | 19 | 36 | 9048 | 1243122 | 133150 | 1.49 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/metrics.test.sh keeps only the floor — the whole-report golden at :2173-2294 (and whatever earlier case it reads its log from), the missing-log exit-1 case and the symlink case — every other contract case cut, no assertion of a kept case changed ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 16 | 32 | 5589 | 1052677 | 134337 | 1.40 | 106 | unknown | unknown | unknown |  |  | full |
| veri/dashboard.py, veri/event_log.py, veri/ledger.py, veri/ledger_steps.py, ledger-steps.sh and lib/exit-contract.sh are unchanged by the branch, and none of the suites issue #930 lists as passing unmodified is changed except missing-argument-exit.test.sh's slice-4 line ⟦diff-checked⟧ ⟦criterion 6⟧ | 4 | 2 | 0 | 0 | 0 | 0 | 84 | 19 | 38 | 6847 | 1032805 | 223585 | 2.13 | 96 | unknown | unknown | unknown |  |  | full |
| the suites issue #930 lists as reading metrics.sh's source or running it pass unmodified against the shim, under the unit-tier guard as #710 left it ⟦full-suite⟧ ⟦criterion 6⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 53 | 16 | 32 | 4720 | 816968 | 214710 | 1.98 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| the port: veri.metrics.main([]) and main([""]) return 2 with stderr exactly "usage: metrics.sh <issue-number>\n", nothing on stdout and no .tdd/ file read; main(["108"]) over a tmp_path working directory holding a one-step .tdd/events.jsonl returns 0 with stdout beginning "### 📊 Metrics — issue 108\n", and main(["108", "extra"]) prints the same stdout; main(["108"]) over a .tdd/issue-108.md mixing an indented "  - [X] …", a "-\t[ ] …", a "* [ ] …", a "- [y] …" and a "text - [ ] …" prints "Steps done: 1 of <n> planned." with <n> = len(veri.ledger.ledger_steps(text)), and "Steps done: 1 of unknown planned." for a ledger with no step line; and pytest cases pin every branch issue #930 lists under "Order matters (#797)" (missing log, non-JSON line and non-object line raising with nothing on stdout; unknown planned count for a directory ledger, NULs dropped, the splitlines over-count; a non-numeric secs leaving the earlier lines on stdout; done/bail/stop with missing keys printing unknown and a resume after a done staying landed; integer status 2 not a kill; the answered-models list split, deduplicated and sorted; the "?" revise budget, the empty-transforms refactor cells, the skipped test-run and unknown tier with padded rows, "Stopped: ?"; two main calls rendering independent reports) — the module carries the whole inline program, imports read_events and ledger_steps and starts no process, and metrics.sh becomes a /bin/sh shim over it in the same commit, its header keeping a lowercase "usage: metrics.sh <issue-number>" line and no issue number; that commit also cuts '#495 the planned-step count is the number of ledger-steps.sh's records, counting no box of its own' from skills/tdd/scripts/tests/metrics.test.sh: replaces 'migration slice 4 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh, metrics.sh leaving slice 4's list and its other scripts staying ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 4/5 | structural-owed | PASS | 0 | 297 | 1.53 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 15 | 15 | 2 | 1 | 1 | 1 | 20 | 0 | 1 | 0 | 4 | 0 | 3 | 11 | 1 | 5 | 0 | 19 | 26 | 13 | 21 | 22 | 25 | 27 | 21 | 21 | 13 | 13 | 1 | 25 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 38 | 1 | 3 |
| target | 15 | 15 | 15 | 15 | 0 | 0 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 1 | 1 | 0 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 45 | 42 | 46 | 50 | 51 | 48 | 47 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 894 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 385 | 740 | 185466 | 25464946 | 2831410 | 31.46 |
