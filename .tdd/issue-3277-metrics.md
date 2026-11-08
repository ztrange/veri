### 📊 Metrics — issue 3277

Wall time for the issue: 991 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.91 over 37 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92827 tokens, largest 146650 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.60 | 92827 |
| 2 | $0.06 | 98623 |
| 3 | $0.03 | 99972 |
| 4 | $0.04 | 102444 |
| 5 | $0.04 | 105102 |
| 6 | $0.03 | 105630 |
| 7 | $0.03 | 106405 |
| 8 | $0.03 | 107069 |
| 9 | $0.03 | 107641 |
| 10 | $0.03 | 108217 |
| 11 | $0.03 | 108895 |
| 12 | $0.06 | 113337 |
| 13 | $0.03 | 114419 |
| 14 | $0.03 | 115739 |
| 15 | $0.03 | 116667 |
| 16 | $0.03 | 117433 |
| 17 | $0.03 | 118346 |
| 18 | $0.03 | 119003 |
| 19 | $0.03 | 119743 |
| 20 | $0.03 | 120782 |
| 21 | $0.03 | 121321 |
| 22 | $0.03 | 121976 |
| 23 | $0.05 | 125777 |
| 24 | $0.05 | 129006 |
| 25 | $0.04 | 130234 |
| 26 | $0.03 | 131196 |
| 27 | $0.04 | 132545 |
| 28 | $0.03 | 133069 |
| 29 | $0.03 | 134054 |
| 30 | $0.03 | 134387 |
| 31 | $0.03 | 134756 |
| 32 | $0.03 | 135396 |
| 33 | $0.06 | 139154 |
| 34 | $0.03 | 139521 |
| 35 | $0.03 | 139870 |
| 36 | $0.04 | 141683 |
| 37 | $0.07 | 146650 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 3 | 3 | 0 | 0 | 31 | 22 | 4 | 8 | 2889 | 18395 | 56797 | 0.17 |
| red | 5 | 2 | 0 | 0 | 304 | 129 | 31 | 60 | 12930 | 639559 | 117987 | 0.68 |
| green | 4 | 1 | 1 | 0 | 1036 | 105 | 42 | 76 | 12771 | 801925 | 79086 | 0.41 |
| red-missing | 1 | 0 | 0 | 0 | 68 | 37 | 9 | 18 | 5104 | 188429 | 27884 | 0.14 |
| pin | 1 | 0 | 1 | 0 | 17 | 10 | 3 | 6 | 1134 | 41032 | 15111 | 0.05 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 3 | 6 | 315 | 42195 | 13825 | 0.04 |
| prose | 11 | 0 | 0 | 0 | 331 | 310 | 11 | 22 | 51375 | 129781 | 322000 | 1.33 |
| skill-edit | 2 | 0 | 0 | 0 | 19 | 14 | 7 | 14 | 1411 | 226658 | 73911 | 0.22 |
| rebase | 4 | 1 | 0 | 0 | 627 | 85 | 40 | 78 | 7964 | 637390 | 94073 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 7 | 2 | 0 | 1103 | 105 | 30 | 60 | 12143 | 400160 | 172435 | 0.59 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 202 | 98 | 21 | 42 | 9409 | 521178 | 69072 | 0.51 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 785 | 189 | 81 | 150 | 21555 | 1447587 | 163256 | 0.77 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 11 | 0.06 |
| green | 1036 | 0.41 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 17 | 0.05 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 107 | 0.47 |
| skill-edit | 0 | 0.00 | 11 | 0.19 |
| rebase | 0 | 0.00 | 452 | 0.18 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When a red-phase leaf (a supervise.sh leaf named develop-red… or revise-red-…) overwrites a tracked production file (a file case_reader.is_test_path does not call a test file) holding the step's uncommitted change, as `git show HEAD:<path> > <path>` does, supervise.sh restores that file to its pre-launch content after the leaf exits; pinned by one case that goes red on the current code, with no change to any graded prose (SKILL.md, SCRIPTS.md or any prompt) ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 277 | 85 | 162 | 31190 | 1694561 | 234554 | 1.26 | 1682 | 1/2 | 0/5 | nothing-left |  |  | full |
| skills/tdd/scripts/prompts/_leaf-safety.md, the safety rules the shared develop prompt includes, states that a leaf never writes a tracked production file from `git show`, `git checkout` or `git restore` (for example `git show HEAD:<path> > <path>`), only reads it ⟦skill-edit⟧ ⟦criterion 2⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 19 | 5 | 10 | 2788 | 36704 | 27111 | 0.10 | 46 | unknown | unknown | unknown |  |  | full |
| fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_build_verify_prompt.py — FAILED test_main_refuses_diff_without_fast_cmd_…_resolves_or_refuses_includes: its "#671 byte-identity" checksums of the rendered verify-green prompt still pin the text before _leaf-safety.md gained the read-only git show/checkout/restore sentence (update the pinned checksums only; no prose or production change) ⟦suite-repair⟧ ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 36 | 15 | 28 | 3904 | 173917 | 75473 | 0.25 | unknown | unknown | unknown | unknown |  |  | full |
| skill-edit step for the unit `skills/tdd/SCRIPTS.md`: change the `supervise.sh` entry so that, beside the sentence on the `mutation-record-restored` event, it states that when a `develop-red…` or `revise-red-…` leaf exits, any tracked production file it changed from the step's uncommitted state is written back and one `production-file-restored` event (`name=`, `file=`) goes to `events.jsonl` per file ⟦skill-edit⟧ ⟦added⟧ ⟦criterion 1⟧ | 4 | 0 | 0 | 0 | 0 | 0 | 110 | 7 | 14 | 18237 | 253930 | 181905 | 0.66 | unknown | unknown | unknown | unknown |  |  | full |
| Go-red: the new production-file restore guard, broken on purpose, makes the first criterion's case fail ⟦human-owed⟧ ⟦criterion 3⟧ | 2 | 0 | 0 | 0 | 0 | 0 | 57 | 28 | 54 | 5124 | 482052 | 37939 | 0.19 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When a red-phase leaf (a supervise.sh leaf named develop-red… or revise-red-…) overwrites a tracked production file (a file case_reader.is_test_path does not call a test file) holding the step's uncommitted change, as `git show HEAD:<path> > <path>` does, supervise.sh restores that file to its pre-launch content after the leaf exits; pinned by one case that goes red on the current code, with no change to any graded prose (SKILL.md, SCRIPTS.md or any prompt) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 20 | 18 | 37 | 9 | 36 | 18 | 18 | 7 | 36 | 42 | 34 |
| fast | 28 | 20 | 28 | 19 | 28 | 21 |  |  |  |  |  |
| target | 2 | 2 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |
| all | 25 | 393 | 21 | 22 | 30 | 20 | 19 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 150 | 288 | 95893 | 2725364 | 800674 | 5.34 (estimate) |
