### 📊 Metrics — issue 1648

Wall time for the issue: 2054 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1031 | 0 | 31013 | 0.09 |
| red | 9 | 4 | 0 | 0 | 644 | 423 | 82 | 162 | 46368 | 3547825 | 298969 | 2.07 |
| green | 10 | 3 | 1 | 0 | 842 | 447 | 87 | 166 | 44176 | 3235956 | 250827 | 1.92 |
| refactor | 6 | 3 | 0 | 0 | 111 | 65 | 23 | 44 | 6173 | 639264 | 104237 | 0.39 |
| exhausted | 1 | 0 | 0 | 0 | 58 | 19 | 3 | 6 | 1329 | 75325 | 14225 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 12 | 11 | 1 | 0 | 334 | 157 | 44 | 84 | 14861 | 1136596 | 208287 | 0.78 |
| developer | claude-sonnet-5-5 | 11 | 0 | 0 | 0 | 722 | 409 | 91 | 180 | 49334 | 3412158 | 315891 | 1.62 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 610 | 397 | 61 | 116 | 34882 | 2949616 | 175093 | 2.16 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 282 | 0.36 |
| green | 0 | 0.00 | 216 | 0.25 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| no-unit-subprocess.test.sh fails, its output naming the suite and its awk scanner's non-zero exit status, when that scanner exits non-zero (a scratch copy of the guard whose awk program is broken, run over a unit/ tree holding a planted offender, goes red rather than reporting a pass), and a scratch copy with the scanner intact still passes on a clean tree; pinned beside the existing plant in unit-subprocess-guard.test.sh ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 106 | 26 | 52 | 9668 | 787003 | 126738 | 0.49 | 270 | unknown | 0/5 | nothing-left |  |  | full |
| no-awk-v-patterns.test.sh, no-docs-reads.test.sh and no-job-spec-kills.test.sh each fail, their output naming the suite and the scanner's non-zero exit status, when a scanner they read through `done < <(…)` exits with a failure status (for grep, a status above 1; grep's 1 for no match stays a clean pass), and each still passes on a clean tree; pinned by driving a scratch copy of each guard with its scanner forced to fail, never by running the real guard over the real tree ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 141 | 34 | 66 | 15972 | 1119843 | 141472 | 0.63 | 449 | 1/2 | 1/5 | nothing-left |  |  | full |
| no-recipe-unit-tier.test.sh, no-sigpipe-pipelines.test.sh and no-size-assertion.test.sh each fail, their output naming the suite and the scanner's non-zero exit status, when a scanner they read through `done < <(…)` exits with a failure status (for grep, a status above 1; grep's 1 for no match stays a clean pass), and each still passes on a clean tree; pinned by driving a scratch copy of each guard with its scanner forced to fail ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 147 | 34 | 66 | 17020 | 1100034 | 124858 | 0.59 | 264 | unknown | 0/5 | nothing-left |  |  | full |
| no-unbacked-pushes.test.sh, missing-argument-exit.test.sh and scratch-copy-libs.test.sh each fail, their output naming the suite and the scanner's non-zero exit status, when a scanner they read through `done < <(…)` exits with a failure status (for grep, a status above 1; grep's 1 for no match stays a clean pass), and each still passes on a clean tree; pinned by driving a scratch copy of each guard with its scanner forced to fail ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 163 | 40 | 78 | 20504 | 1541874 | 100097 | 0.61 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| no-unit-subprocess.test.sh fails, its output naming the suite and its awk scanner's non-zero exit status, when that scanner exits non-zero (a scratch copy of the guard whose awk program is broken, run over a unit/ tree holding a planted offender, goes red rather than reporting a pass), and a scratch copy with the scanner intact still passes on a clean tree; pinned beside the existing plant in unit-subprocess-guard.test.sh ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 24 | 0.11 |
| no-awk-v-patterns.test.sh, no-docs-reads.test.sh and no-job-spec-kills.test.sh each fail, their output naming the suite and the scanner's non-zero exit status, when a scanner they read through `done < <(…)` exits with a failure status (for grep, a status above 1; grep's 1 for no match stays a clean pass), and each still passes on a clean tree; pinned by driving a scratch copy of each guard with its scanner forced to fail, never by running the real guard over the real tree ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 52 | 0.16 |
| no-recipe-unit-tier.test.sh, no-sigpipe-pipelines.test.sh and no-size-assertion.test.sh each fail, their output naming the suite and the scanner's non-zero exit status, when a scanner they read through `done < <(…)` exits with a failure status (for grep, a status above 1; grep's 1 for no match stays a clean pass), and each still passes on a clean tree; pinned by driving a scratch copy of each guard with its scanner forced to fail ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 35 | 0.12 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 2 | 2 | 1 | 0 | 4 | 3 | 3 | 2 | 0 | 5 | 5 | 4 | 28 | 37 |
| fast | 7 | 7 | 6 | 6 | 7 | 7 | 7 | 6 | 7 | 13 |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 2 | 3 | 36 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 196 | 380 | 99077 | 7498370 | 699271 | 4.57 |
