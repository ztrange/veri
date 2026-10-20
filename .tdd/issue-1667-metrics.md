### 📊 Metrics — issue 1667

Wall time for the issue: 750 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 4 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 32 | 27 | 5 | 10 | 2780 | 128697 | 30650 | 0.12 |
| red | 3 | 1 | 0 | 0 | 77 | 53 | 13 | 26 | 6903 | 405752 | 61346 | 0.26 |
| green | 2 | 1 | 0 | 0 | 67 | 27 | 11 | 18 | 2707 | 253990 | 30506 | 0.13 |
| refactor | 2 | 1 | 0 | 0 | 63 | 29 | 11 | 20 | 3170 | 296444 | 32399 | 0.14 |
| pin | 1 | 1 | 0 | 0 | 13 | 10 | 3 | 6 | 1325 | 77465 | 14599 | 0.06 |
| diff | 6 | 0 | 3 | 0 | 146 | 99 | 23 | 46 | 7697 | 642914 | 64926 | 0.43 |
| exhausted | 1 | 0 | 0 | 0 | 14 | 12 | 2 | 4 | 815 | 45730 | 11121 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 5 | 4 | 0 | 166 | 105 | 29 | 58 | 10037 | 779534 | 105934 | 0.44 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 123 | 71 | 23 | 40 | 9115 | 629257 | 79232 | 0.35 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 123 | 81 | 16 | 32 | 6245 | 442201 | 60381 | 0.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 146 | 0.43 |
| exhausted | 0 | 0.00 | 14 | 0.08 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A bash suite run by mutation-parity.sh sees no VERI_* or CLAUDE_* variable from the caller's environment except VERI_VENV: with a VERI_* tunable set in the caller, a planted bash suite that fails when it sees any VERI_*/CLAUDE_* variable other than VERI_VENV passes its unmutated run (a process case in tests/py/test_mutation_parity_process.py, marked process) ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 85 | 29 | 52 | 9613 | 752631 | 100232 | 0.42 | 302 | unknown | 1/5 | nothing-structural |  |  | full |
| A pytest case run by mutation-parity.sh sees no VERI_* or CLAUDE_* variable from the caller's environment except VERI_VENV, and the pytest leg still finds its interpreter through VERI_VENV: with a VERI_* tunable set in the caller, a planted pytest case that fails when it sees one passes its unmutated run (a process case in tests/py/test_mutation_parity_process.py, marked process) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 9 | 18 | 4492 | 281020 | 38618 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| mutation-parity.sh's exit codes and report are otherwise unchanged with the strip in place: run with a VERI_* tunable set in the caller, a proven row still prints its report line ending in proven and exits 0, and an owed or unproven row still exits 1 — the branch's diff adds one process case to tests/py/test_mutation_parity_process.py pinning it, no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 7 | 0 | 3 | 0 | 0 | 0 | 111 | 25 | 50 | 8512 | 688644 | 76047 | 0.51 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A bash suite run by mutation-parity.sh sees no VERI_* or CLAUDE_* variable from the caller's environment except VERI_VENV: with a VERI_* tunable set in the caller, a planted bash suite that fails when it sees any VERI_*/CLAUDE_* variable other than VERI_VENV passes its unmutated run (a process case in tests/py/test_mutation_parity_process.py, marked process) ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 63 | 0.14 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 0 | 10 | 10 | 12 | 12 | 4 | 6 | 6 | 5 |
| fast | 6 | 5 | 6 | 6 | 6 | 6 |  |  |  |  |  |
| target | 1 | 0 | 1 | 0 |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 68 | 130 | 25397 | 1850992 | 245547 | 1.22 |
