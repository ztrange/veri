### 📊 Metrics — issue 3277

Wall time for the issue: 1773 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3281.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.83 over 72 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92827 tokens, largest 149373 tokens
Conductor context: first turn 92831 tokens, largest 126768 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.61 | 92827 |
| 2 | $0.08 | 98623 |
| 3 | $0.04 | 99972 |
| 4 | $0.05 | 102444 |
| 5 | $0.05 | 105102 |
| 6 | $0.03 | 105630 |
| 7 | $0.04 | 106405 |
| 8 | $0.04 | 107069 |
| 9 | $0.03 | 107641 |
| 10 | $0.04 | 108217 |
| 11 | $0.04 | 108895 |
| 12 | $0.06 | 113337 |
| 13 | $0.04 | 114419 |
| 14 | $0.05 | 115739 |
| 15 | $0.04 | 116667 |
| 16 | $0.04 | 117433 |
| 17 | $0.04 | 118346 |
| 18 | $0.04 | 119003 |
| 19 | $0.04 | 119743 |
| 20 | $0.04 | 120782 |
| 21 | $0.04 | 121321 |
| 22 | $0.04 | 121976 |
| 23 | $0.06 | 125777 |
| 24 | $0.06 | 129006 |
| 25 | $0.05 | 130234 |
| 26 | $0.04 | 131196 |
| 27 | $0.05 | 132545 |
| 28 | $0.04 | 133069 |
| 29 | $0.04 | 134054 |
| 30 | $0.04 | 134387 |
| 31 | $0.04 | 134756 |
| 32 | $0.04 | 135396 |
| 33 | $0.07 | 139154 |
| 34 | $0.04 | 139521 |
| 35 | $0.04 | 139870 |
| 36 | $0.05 | 141683 |
| 37 | $0.08 | 146650 |
| 38 | $0.06 | 148468 |
| 39 | $0.04 | 149373 |
| 40 | $0.60 | 92831 |
| 41 | $0.07 | 98811 |
| 42 | $0.03 | 100158 |
| 43 | $0.04 | 102050 |
| 44 | $0.04 | 104661 |
| 45 | $0.03 | 105700 |
| 46 | $0.03 | 106342 |
| 47 | $0.02 | 106803 |
| 48 | $0.02 | 107112 |
| 49 | $0.03 | 107587 |
| 50 | $0.03 | 108240 |
| 51 | $0.06 | 112453 |
| 52 | $0.03 | 112778 |
| 53 | $0.03 | 114176 |
| 54 | $0.03 | 114624 |
| 55 | $0.03 | 115130 |
| 56 | $0.03 | 115624 |
| 57 | $0.03 | 116281 |
| 58 | $0.06 | 120811 |
| 59 | $0.03 | 121725 |
| 60 | $0.04 | 123175 |
| 61 | $0.03 | 124158 |
| 62 | $0.03 | 125158 |
| 63 | $0.03 | 125572 |
| 64 | $0.03 | 126004 |
| 65 | $0.03 | 126475 |
| 66 | $0.03 | 126768 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 4 | 4 | 0 | 0 | 44 | 31 | 5 | 10 | 4123 | 18395 | 75552 | 0.23 |
| red | 5 | 2 | 0 | 0 | 304 | 129 | 31 | 60 | 12930 | 639559 | 117987 | 0.68 |
| green | 4 | 1 | 1 | 0 | 1036 | 105 | 42 | 76 | 12771 | 801925 | 79086 | 0.41 |
| red-missing | 1 | 0 | 0 | 0 | 68 | 37 | 9 | 18 | 5104 | 188429 | 27884 | 0.14 |
| pin | 1 | 0 | 1 | 0 | 17 | 10 | 3 | 6 | 1134 | 41032 | 15111 | 0.05 |
| refactor | 1 | 0 | 0 | 0 | 7 | 4 | 3 | 6 | 315 | 42195 | 13825 | 0.04 |
| prose | 15 | 0 | 0 | 0 | 484 | 452 | 15 | 30 | 74679 | 134978 | 499528 | 2.01 |
| skill-edit | 2 | 0 | 0 | 0 | 19 | 14 | 7 | 14 | 1411 | 226658 | 73911 | 0.22 |
| rebase | 6 | 2 | 0 | 0 | 990 | 121 | 55 | 108 | 10965 | 868387 | 137219 | 0.54 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 9 | 2 | 0 | 1364 | 128 | 36 | 72 | 14466 | 465326 | 213618 | 0.73 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 202 | 98 | 21 | 42 | 9409 | 521178 | 69072 | 0.51 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 900 | 211 | 91 | 170 | 23467 | 1613418 | 183974 | 0.86 |

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
| Go-red: the new production-file restore guard, broken on purpose, makes the first criterion's case fail ⟦human-owed⟧ ⟦criterion 3⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 93 | 43 | 84 | 8125 | 713049 | 81085 | 0.36 | unknown | unknown | unknown | unknown |  |  | full |

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
| all | 25 | 393 | 21 | 22 | 30 | 20 | 19 | 37 | 28 | 229 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 170 | 328 | 123432 | 2961558 | 1040103 | 8.15 (estimate) |
