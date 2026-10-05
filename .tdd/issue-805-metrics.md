### 📊 Metrics — issue 805

Wall time for the issue: 6594 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 11 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/912.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 53 | 45 | 5 | 10 | 4246 | 262530 | 55267 | 0.58 |
| red | 13 | 5 | 0 | 0 | 808 | 614 | 120 | 234 | 56225 | 7066842 | 744595 | 8.50 |
| pin | 3 | 3 | 0 | 0 | 121 | 80 | 17 | 34 | 8189 | 882869 | 157723 | 1.60 |
| green | 12 | 5 | 1 | 0 | 1470 | 439 | 100 | 198 | 41003 | 5595526 | 588510 | 6.65 |
| refactor | 10 | 5 | 0 | 0 | 712 | 228 | 55 | 110 | 20110 | 2854147 | 515700 | 5.10 |
| diff | 6 | 3 | 0 | 0 | 346 | 120 | 27 | 52 | 10403 | 1318892 | 308926 | 2.94 |
| predicate | 1 | 0 | 0 | 0 | 16 | 10 | 2 | 4 | 908 | 69035 | 46216 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 23 | 22 | 1 | 0 | 1803 | 686 | 145 | 286 | 64703 | 7582564 | 1143418 | 11.96 |
| developer | claude-opus-5-5 | 23 | 0 | 0 | 0 | 1723 | 850 | 181 | 356 | 76381 | 10467277 | 1273519 | 13.81 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 538 | 2.15 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `run-affordable.sh two`, with VERI_STEP_BUDGET and VERI_RUN_BUDGET unset, exits 2 with nothing on stdout and stderr byte for byte the two lines `run-affordable.sh: <steps-remaining> is not a whole number: 'two'` then `usage: run-affordable.sh <steps-remaining> (a whole number)` — a case in tests/unit/run-affordable.test.sh written against the bash script, before the port ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 12 | 24 | 5296 | 647853 | 104202 | 1.07 | unknown | unknown | unknown | unknown |  |  | pin |
| `run-affordable.sh`, run through a symlink to the skill directory and from another working directory holding its own .tdd/events.jsonl, answers exactly as when run in place — exit 1 with the same four figures for a projection over VERI_RUN_BUDGET, and from a directory with no .tdd/events.jsonl exit 2 with nothing on stdout and step-cost.sh's `cannot read .tdd/events.jsonl in <dir>` line naming that directory — a case in tests/unit/run-affordable.test.sh written before the port ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 114 | 19 | 36 | 9443 | 1117850 | 120205 | 1.37 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_run_affordable.py: veri.run_affordable.main(argv), with subprocess faked in-process, returns 2 with no subprocess call, nothing on stdout and stderr `run-affordable.sh: <steps-remaining> is not a whole number: ''` then `usage: run-affordable.sh <steps-remaining> (a whole number)` for [] and for [""], and the same with 'two' for ["two"]; returns 1 printing `spent 22.50, steps remaining 4, median 7.50, projection 52.50` for ["4"] against a faked step-budget.sh answering `12` and `50` and a faked step-cost.sh --steps answering `5.25 6`, `7.50 6`, `9.75 6`; returns 3 with nothing on stdout when the faked step-cost.sh --steps answers only two-leaf lines; no return code outside 0–3; run-affordable.sh is removed from migration slice 7's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying and nothing else in that suite changing: replaces 'migration slice 7 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 288 | 64 | 126 | 26931 | 3603218 | 383808 | 4.33 | 873 | 1/2 | 0/5 | structural-owed |  |  | full |
| tests/py/test_run_affordable.py pins through veri.run_affordable.main how the siblings are called and answered, with subprocess faked in-process: step-budget.sh (no argument) runs before step-cost.sh --steps, both resolved beside the module's own scripts directory and run in the caller's working directory and environment; the ceiling is the last line of step-budget.sh's stdout; a sibling's status 0–3 passes through unchanged — step-budget.sh's 2 returns 2 without step-cost.sh running, step-cost.sh's 3 returns 3, its 2 returns 2 and its 1 returns 1, each with nothing on stdout — and a sibling status outside 0–3 (5) returns 2 ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 230 | 42 | 84 | 19312 | 2377874 | 324024 | 3.45 | 553 | unknown | 1/5 | nothing-structural |  |  | full |
| tests/py/test_run_affordable.py pins through veri.run_affordable.main the reading of <steps-remaining>: it is checked before either sibling runs (a bad argument with VERI_RUN_BUDGET=fifty prints only the refusal); ` 3`, `--`, `1.5`, `-1` and "3\n" are refused with exit 2, the argument echoed byte for byte, a newline inside it included, and a non-UTF-8 byte (b"\xff" in argv) echoed as that raw byte, never as `\udcff`; `007` is accepted and printed as `steps remaining 7`; arguments after the first are ignored, so ["3", "extra"] answers as ["3"] ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 190 | 50 | 96 | 18972 | 2747285 | 321354 | 3.50 | 598 | unknown | 0/5 | nothing-left |  |  | full |
| tests/py/test_run_affordable.py pins through veri.run_affordable.main the projection rule: a step is full only with more than two leaves, and only full steps enter the median while every step's dollars, pins included, count toward spent; the median is the middle full step, or for an even count the mean of the middle two in ascending order; no full step returns 3 printing nothing whatever has been spent (two pins of 100 against a ceiling of 1); the comparison is strict, so spent 9.00 with 0 steps remaining against a ceiling of 9 returns 0 and 8.99 against 8.98 returns 1; a return of 0 prints nothing on stdout or stderr ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 166 | 38 | 76 | 14725 | 2022316 | 313175 | 3.20 | 469 | unknown | 0/5 | nothing-left |  |  | full |
| tests/py/test_run_affordable.py pins through veri.run_affordable.main the figures' arithmetic and format as the awk did it: the per-step lines are summed and the median taken in `sort -n` order (ascending dollars, ties by whole line) in IEEE doubles, so medians 1.01 and 1.02 print `median 1.02`; figures are formatted with `%.2f` and never localised (LC_ALL=de_DE.UTF-8 still prints `spent 3.00`, the C-locale form `make test` runs under); a count past 2^63 prints `steps remaining -9223372036854775808` as macOS awk's `%d` wraps it; with its stdout file descriptor closed, the over-ceiling path returns 2 as awk's failed close did, and the within-ceiling path returns 0 ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 224 | 51 | 102 | 21118 | 2918308 | 321355 | 3.58 | 590 | unknown | 1/5 | nothing-structural |  |  | full |
| run-affordable.sh is a /bin/sh shim that execs python3 on veri/run_affordable.py once per invocation, holding no Python source, keeping the lowercase header line `usage: run-affordable.sh <steps-remaining> (a whole number)`, citing no issue number in its header; veri/run_affordable.py starts no sort, awk or python3 child, imports neither sibling, and has no wrapper turning an uncaught exception into exit 2; every case in tests/unit/run-affordable.test.sh passes with its assertions unmodified against the shim, the port commit touching suites only in copy lines and stub libs, and coming before any cut ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 14 | 26 | 5316 | 744650 | 114604 | 1.17 | 209 | unknown | unknown | unknown |  |  | full |
| tests/py/test_run_affordable.py asserts in-process, through veri.run_affordable.main with only subprocess (step-budget.sh and step-cost.sh --steps), argv and the environment faked and no function of veri.run_affordable patched, what the bash cases at tests/unit/run-affordable.test.sh :84-92, :101-113, :127-134, :136-140, :142-149, :151-163 and :165-171 (as numbered at the plan commit) assert, asserting main's return code wherever the bash case asserts the exit code ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 96 | 16 | 32 | 9730 | 964680 | 118405 | 1.33 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/unit/run-affordable.test.sh no longer holds the seven cases at :84-92, :101-113, :127-134, :136-140, :142-149, :151-163 and :165-171 (as numbered at the plan commit), and keeps the floor and survivors — 'a projection over VERI_RUN_BUDGET exits 1 printing spent, steps remaining, median and projection' (exit 1), 'a projection within VERI_RUN_BUDGET exits 0 printing nothing' (exit 0), 'no completed full step, only pins or no usage at all, exits 3 printing nothing' (exit 3), the bad-argument stderr case (exit 2) and the symlink case — with no remaining case's assertions changed by the branch and its sweepable report still empty ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 7 | 14 | 3188 | 322544 | 101610 | 0.94 | 92 | unknown | unknown | unknown |  |  | full |
| step-budget.sh, step-cost.sh, veri/step_cost.py, tests/unit/exit-contract.test.sh and tests/py/test_comment_class.py are unchanged by the branch, and tests/unit/missing-argument-exit.test.sh changes only in migration slice 7's script list ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 6 | 12 | 1899 | 251698 | 92712 | 0.83 | 115 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| tests/py/test_run_affordable.py: veri.run_affordable.main(argv), with subprocess faked in-process, returns 2 with no subprocess call, nothing on stdout and stderr `run-affordable.sh: <steps-remaining> is not a whole number: ''` then `usage: run-affordable.sh <steps-remaining> (a whole number)` for [] and for [""], and the same with 'two' for ["two"]; returns 1 printing `spent 22.50, steps remaining 4, median 7.50, projection 52.50` for ["4"] against a faked step-budget.sh answering `12` and `50` and a faked step-cost.sh --steps answering `5.25 6`, `7.50 6`, `9.75 6`; returns 3 with nothing on stdout when the faked step-cost.sh --steps answers only two-leaf lines; no return code outside 0–3; run-affordable.sh is removed from migration slice 7's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying and nothing else in that suite changing: replaces 'migration slice 7 sources lib/exit-contract.sh and refuses through it, with no hand-built usage-and-exit idiom left' in skills/tdd/scripts/tests/unit/missing-argument-exit.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 129 | 0.98 |
| tests/py/test_run_affordable.py pins through veri.run_affordable.main how the siblings are called and answered, with subprocess faked in-process: step-budget.sh (no argument) runs before step-cost.sh --steps, both resolved beside the module's own scripts directory and run in the caller's working directory and environment; the ceiling is the last line of step-budget.sh's stdout; a sibling's status 0–3 passes through unchanged — step-budget.sh's 2 returns 2 without step-cost.sh running, step-cost.sh's 3 returns 3, its 2 returns 2 and its 1 returns 1, each with nothing on stdout — and a sibling status outside 0–3 (5) returns 2 ⟦criterion 5⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 152 | 1.07 |
| tests/py/test_run_affordable.py pins through veri.run_affordable.main the reading of <steps-remaining>: it is checked before either sibling runs (a bad argument with VERI_RUN_BUDGET=fifty prints only the refusal); ` 3`, `--`, `1.5`, `-1` and "3\n" are refused with exit 2, the argument echoed byte for byte, a newline inside it included, and a non-UTF-8 byte (b"\xff" in argv) echoed as that raw byte, never as `\udcff`; `007` is accepted and printed as `steps remaining 7`; arguments after the first are ignored, so ["3", "extra"] answers as ["3"] ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 182 | 0.98 |
| tests/py/test_run_affordable.py pins through veri.run_affordable.main the projection rule: a step is full only with more than two leaves, and only full steps enter the median while every step's dollars, pins included, count toward spent; the median is the middle full step, or for an even count the mean of the middle two in ascending order; no full step returns 3 printing nothing whatever has been spent (two pins of 100 against a ceiling of 1); the comparison is strict, so spent 9.00 with 0 steps remaining against a ceiling of 9 returns 0 and 8.99 against 8.98 returns 1; a return of 0 prints nothing on stdout or stderr ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 124 | 1.02 |
| tests/py/test_run_affordable.py pins through veri.run_affordable.main the figures' arithmetic and format as the awk did it: the per-step lines are summed and the median taken in `sort -n` order (ascending dollars, ties by whole line) in IEEE doubles, so medians 1.01 and 1.02 print `median 1.02`; figures are formatted with `%.2f` and never localised (LC_ALL=de_DE.UTF-8 still prints `spent 3.00`, the C-locale form `make test` runs under); a count past 2^63 prints `steps remaining -9223372036854775808` as macOS awk's `%d` wraps it; with its stdout file descriptor closed, the over-ceiling path returns 2 as awk's failed close did, and the within-ceiling path returns 0 ⟦criterion 5⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 125 | 1.05 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 3 | 11 | 12 | 13 | 11 | 10 | 10 | 15 | 1 | 1 | 0 | 3 | 4 | 11 | 4 | 0 | 1 | 4 | 1 | 1 | 29 | 1 | 3 | 6 | 4 | 0 | 1 | 1 | 1 | 4 | 4 | 4 | 1 | 1 | 4 | 5 | 4 | 4 | 63 | 1 | 1 | 15 | 61 |
| target | 3 | 3 | 3 | 3 | 1 | 3 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 63 | 61 | 63 | 62 | 63 | 61 | 62 | 61 | 63 | 61 | 61 | 62 | 61 | 62 | 62 | 62 | 62 | 62 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 326 | 642 | 141084 | 18049841 | 2416937 | 25.77 |
