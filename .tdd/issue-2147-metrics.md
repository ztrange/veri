### 📊 Metrics — issue 2147

Wall time for the issue: 1591 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 7 planned.
Outcome: the run bailed — needs-user, a process failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.96 over 67 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92139 tokens, largest 170248 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.60 | 92139 |
| 2 | $0.02 | 92695 |
| 3 | $0.04 | 95014 |
| 4 | $0.03 | 96926 |
| 5 | $0.02 | 97274 |
| 6 | $0.02 | 97744 |
| 7 | $0.02 | 98040 |
| 8 | $0.02 | 98282 |
| 9 | $0.02 | 98575 |
| 10 | $0.02 | 98871 |
| 11 | $0.03 | 99561 |
| 12 | $0.02 | 99917 |
| 13 | $0.03 | 101585 |
| 14 | $0.03 | 103340 |
| 15 | $0.03 | 105042 |
| 16 | $0.03 | 106344 |
| 17 | $0.03 | 107483 |
| 18 | $0.02 | 107897 |
| 19 | $0.09 | 116157 |
| 20 | $0.05 | 119280 |
| 21 | $0.04 | 121538 |
| 22 | $0.03 | 122801 |
| 23 | $0.03 | 123521 |
| 24 | $0.03 | 124154 |
| 25 | $0.03 | 124564 |
| 26 | $0.03 | 124926 |
| 27 | $0.03 | 125703 |
| 28 | $0.03 | 126898 |
| 29 | $0.03 | 127837 |
| 30 | $0.03 | 128241 |
| 31 | $0.03 | 128774 |
| 32 | $0.03 | 129601 |
| 33 | $0.03 | 130313 |
| 34 | $0.04 | 131488 |
| 35 | $0.03 | 132089 |
| 36 | $0.03 | 133142 |
| 37 | $0.03 | 133874 |
| 38 | $0.03 | 134262 |
| 39 | $0.04 | 135343 |
| 40 | $0.04 | 136634 |
| 41 | $0.05 | 139156 |
| 42 | $0.03 | 139905 |
| 43 | $0.03 | 140235 |
| 44 | $0.03 | 141035 |
| 45 | $0.04 | 142189 |
| 46 | $0.03 | 142573 |
| 47 | $0.04 | 143501 |
| 48 | $0.04 | 144493 |
| 49 | $0.04 | 145599 |
| 50 | $0.04 | 146432 |
| 51 | $0.04 | 147706 |
| 52 | $0.03 | 148078 |
| 53 | $0.04 | 149325 |
| 54 | $0.04 | 150440 |
| 55 | $0.04 | 151234 |
| 56 | $0.04 | 152141 |
| 57 | $0.04 | 152860 |
| 58 | $0.04 | 154647 |
| 59 | $0.06 | 157908 |
| 60 | $0.04 | 159176 |
| 61 | $0.04 | 160516 |
| 62 | $0.05 | 162283 |
| 63 | $0.04 | 163088 |
| 64 | $0.04 | 163993 |
| 65 | $0.04 | 165256 |
| 66 | $0.07 | 169754 |
| 67 | $0.04 | 170248 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 24 | 20 | 5 | 10 | 2438 | 142607 | 38243 | 0.13 |
| red | 8 | 2 | 0 | 0 | 236 | 148 | 43 | 86 | 18331 | 1375676 | 181288 | 0.77 |
| green | 4 | 2 | 0 | 0 | 360 | 47 | 18 | 36 | 5474 | 543588 | 71910 | 0.29 |
| refactor | 2 | 0 | 0 | 0 | 13 | 7 | 5 | 10 | 410 | 131192 | 31041 | 0.09 |
| pin | 3 | 3 | 0 | 0 | 52 | 30 | 11 | 22 | 3526 | 283471 | 63883 | 0.22 |
| prose | 3 | 0 | 0 | 0 | 297 | 279 | 3 | 6 | 45949 | 3785 | 297178 | 1.20 |
| skill-edit | 1 | 0 | 0 | 0 | 49 | 19 | 6 | 12 | 2202 | 674158 | 116512 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 216 | 92 | 30 | 60 | 10705 | 812334 | 167765 | 0.61 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 469 | 160 | 52 | 104 | 19474 | 1664200 | 218600 | 0.91 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 30 | 0.12 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A new executable bash script `skills/tdd/scripts/pr-ready.sh <pr-number> <sha>` sources `lib/github.sh` itself and calls `gh_pr_ready`; run from `zsh -c` against a stubbed `gh` on PATH it marks a draft PR ready and exits 0 (a process case in a pytest suite under `skills/tdd/scripts/tests/py/`, skipped when no zsh is installed); called with no argument it prints a usage line and exits 2, and its entry in `skills/tdd/SCRIPTS.md` declares its caller ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 57 | 19 | 38 | 6426 | 547245 | 107874 | 0.39 | 416 | unknown | 0/5 | nothing-left |  |  | full |
| In the same suite as the pr-ready.sh zsh case, a case shows that sourcing `lib/github.sh` and calling `gh_pr_ready` under `zsh -c` against the same stubbed `gh` fails, so the suite is known to detect the bug (skipped when no zsh is installed; no production change) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 10 | 20 | 3957 | 301933 | 35734 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| `wait-ci.sh <pr-url> <slice> "" <sha>` on a PR the pull read reports as a draft exits 2, prints a message on stderr naming "draft", and creates no `.tdd/ci-deadline-<sha>` file; the Red supersedes the draft rows of `test_main_records_no_deadline_on_a_draft_pr_and_counts_one_from_its_first_ready_call_issue_894` in `skills/tdd/scripts/tests/py/unit/test_wait_ci.py`, which expect exit 3 for a draft, rather than adding a case contradicting them ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 55 | 20 | 40 | 6198 | 582043 | 87457 | 0.34 | 281 | unknown | 0/5 | nothing-left |  |  | full |
| `wait-ci.sh` on a non-draft PR behaves as before: it writes `.tdd/ci-deadline-<sha>` and keeps its exit codes 0 green, 1 red, 2 past the deadline, 3 still pending (no production change) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 15 | 30 | 5354 | 521933 | 43511 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/tdd/SKILL.md`: replace DP44 and add DP81 in `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SKILL.md` with the issue's rows exactly as they appear, edit the Draft PR step's ready line to run `$S/pr-ready.sh <pr-number> "$(git rev-parse HEAD)"` as a command, never sourcing `lib/github.sh`, and to bail as a system failure (`no-verdict`) with the PR left a draft, before `wait-ci.sh` runs, when it exits non-zero; grade the unit PASS against its whole list and sign it; updating the pins in `skills/tdd/scripts/tests/py/unit/test_skill_draft_pr.py` and `skills/tdd/scripts/tests/py/unit/test_skill_draft_pr_readers.py` ⟦skill-edit⟧ ⟦criterion 6⟧ | 4 | 0 | 0 | 0 | 0 | 0 | 298 | 9 | 18 | 48151 | 677943 | 413690 | 1.58 | 419 | unknown | unknown | unknown |  |  | full |
| A case reads `skills/tdd/SKILL.md` and fails when any line matches `\. \$S/lib/github.sh`, i.e. when SKILL.md marks the PR ready by sourcing `lib/github.sh` rather than running a script ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 7 | 14 | 2476 | 177642 | 48941 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| A case runs the Draft PR step's ready line and the `wait-ci.sh` line after it from `skills/tdd/SKILL.md` under bash against a `pr-ready.sh` stub that exits non-zero and a `wait-ci.sh` stub that records being called, and shows `wait-ci.sh` never runs and no `.tdd/ci-deadline-<sha>` is written ⟦criterion 5⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 25 | 6 | 12 | 3330 | 203131 | 24605 | 0.12 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A new executable bash script `skills/tdd/scripts/pr-ready.sh <pr-number> <sha>` sources `lib/github.sh` itself and calls `gh_pr_ready`; run from `zsh -c` against a stubbed `gh` on PATH it marks a draft PR ready and exits 0 (a process case in a pytest suite under `skills/tdd/scripts/tests/py/`, skipped when no zsh is installed); called with no argument it prints a usage line and exits 2, and its entry in `skills/tdd/SCRIPTS.md` declares its caller ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |
| `wait-ci.sh <pr-url> <slice> "" <sha>` on a PR the pull read reports as a draft exits 2, prints a message on stderr naming "draft", and creates no `.tdd/ci-deadline-<sha>` file; the Red supersedes the draft rows of `test_main_records_no_deadline_on_a_draft_pr_and_counts_one_from_its_first_ready_call_issue_894` in `skills/tdd/scripts/tests/py/unit/test_wait_ci.py`, which expect exit 3 for a draft, rather than adding a case contradicting them ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 6 | 13 | 132 | 6 | 14 | 2 | 4 | 3 | 4 | 5 | 1 | 2 |
| fast | 25 | 26 | 54 | 26 |  |  |  |  |  |  |  |  |
| target | 1 | 3 | 1 | 2 | 1 | 1 | 1 | 4 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 91 | 182 | 78330 | 3154477 | 800055 | 3.10 |
