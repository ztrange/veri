### 📊 Metrics — issue 3277

Wall time for the issue: 2611 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 4 planned.
Outcome: the run bailed — untestable-criterion, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 9 | 6 | 2 | 4 | 796 | 18395 | 19448 | 0.06 |
| red | 5 | 2 | 0 | 0 | 304 | 129 | 31 | 60 | 12930 | 639559 | 117987 | 0.68 |
| green | 4 | 1 | 1 | 0 | 1036 | 105 | 42 | 76 | 12771 | 801925 | 79086 | 0.41 |
| red-missing | 1 | 0 | 0 | 0 | 68 | 37 | 9 | 18 | 5104 | 188429 | 27884 | 0.14 |
| pin | 1 | 0 | 1 | 0 | 17 | 10 | 3 | 6 | 1134 | 41032 | 15111 | 0.05 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 3 | 6 | 315 | 42195 | 13825 | 0.04 |
| prose | 2 | 0 | 0 | 0 | 17 | 13 | 2 | 4 | 2106 | 2165 | 17879 | 0.07 |
| skill-edit | 1 | 0 | 0 | 0 | 8 | 6 | 3 | 6 | 682 | 34539 | 9232 | 0.03 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 4 | 2 | 0 | 670 | 75 | 23 | 46 | 8675 | 349966 | 97990 | 0.37 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 202 | 98 | 21 | 42 | 9409 | 521178 | 69072 | 0.51 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 569 | 118 | 46 | 82 | 14966 | 860391 | 106279 | 0.50 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 11 | 0.06 |
| green | 1036 | 0.41 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 17 | 0.05 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When a red-phase leaf (a supervise.sh leaf named develop-red… or revise-red-…) overwrites a tracked production file (a file case_reader.is_test_path does not call a test file) holding the step's uncommitted change, as `git show HEAD:<path> > <path>` does, supervise.sh restores that file to its pre-launch content after the leaf exits; pinned by one case that goes red on the current code, with no change to any graded prose (SKILL.md, SCRIPTS.md or any prompt) ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 277 | 85 | 162 | 31190 | 1694561 | 234554 | 1.26 | 1682 | 1/2 | 0/5 | nothing-left |  |  | full |
| skills/tdd/scripts/prompts/_leaf-safety.md, the safety rules the shared develop prompt includes, states that a leaf never writes a tracked production file from `git show`, `git checkout` or `git restore` (for example `git show HEAD:<path> > <path>`), only reads it ⟦skill-edit⟧ ⟦criterion 2⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 19 | 5 | 10 | 2788 | 36704 | 27111 | 0.10 | 46 | unknown | unknown | unknown |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py — FAILED test_main_refuses_diff_without_fast_cmd_…_resolves_or_refuses_includes: its "#671 byte-identity" checksums of the rendered verify-green prompt still pin the text before _leaf-safety.md gained the read-only git show/checkout/restore sentence (update the pinned checksums only; no prose or production change) ⟦suite-repair⟧ ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 8 | 3 | 4 | 1064 | 18579 | 19339 | 0.06 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When a red-phase leaf (a supervise.sh leaf named develop-red… or revise-red-…) overwrites a tracked production file (a file case_reader.is_test_path does not call a test file) holding the step's uncommitted change, as `git show HEAD:<path> > <path>` does, supervise.sh restores that file to its pre-launch content after the leaf exits; pinned by one case that goes red on the current code, with no change to any graded prose (SKILL.md, SCRIPTS.md or any prompt) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 20 | 18 | 37 | 9 | 36 | 18 | 18 | 7 | 36 | 42 | 34 |
| fast | 28 | 20 | 28 | 19 | 28 | 21 |  |  |  |  |  |
| target | 2 | 2 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 95 | 180 | 35838 | 1768239 | 300452 | 1.48 |
