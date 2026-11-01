### 📊 Metrics — issue 2728

Wall time for the issue: 1902 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2869.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.33 over 19 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87059 tokens, largest 131974 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 87059 |
| 2 | $0.07 | 94157 |
| 3 | $0.04 | 96408 |
| 4 | $0.04 | 98427 |
| 5 | $0.03 | 99814 |
| 6 | $0.05 | 103398 |
| 7 | $0.06 | 108344 |
| 8 | $0.05 | 112050 |
| 9 | $0.04 | 114194 |
| 10 | $0.04 | 115728 |
| 11 | $0.10 | 125412 |
| 12 | $0.04 | 126963 |
| 13 | $0.04 | 128491 |
| 14 | $0.03 | 129206 |
| 15 | $0.03 | 129800 |
| 16 | $0.03 | 130519 |
| 17 | $0.03 | 130898 |
| 18 | $0.03 | 131151 |
| 19 | $0.03 | 131974 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 11 | 2 | 4 | 1409 | 31244 | 32473 | 0.10 |
| prose | 5 | 0 | 0 | 0 | 115 | 91 | 5 | 10 | 14530 | 32785 | 159647 | 0.55 |
| skill-edit | 1 | 0 | 0 | 0 | 12 | 7 | 4 | 8 | 634 | 186947 | 63004 | 0.18 |
| red | 1 | 0 | 0 | 0 | 35 | 18 | 6 | 12 | 2542 | 186215 | 18645 | 0.09 |
| pin | 1 | 1 | 0 | 0 | 29 | 12 | 4 | 8 | 1460 | 108832 | 15367 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 43 | 23 | 6 | 12 | 2869 | 140076 | 47840 | 0.16 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 35 | 18 | 6 | 12 | 2542 | 186215 | 18645 | 0.09 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-edit step for the unit `skills/tdd/SCRIPTS.md`: row SC23 of `skills/tdd/REQUIREMENTS.md` is replaced by the row the issue states, and SCRIPTS.md's `add-ledger-step.sh` entry states among its exit-2 refusals that a text already carrying a `⟦criterion k⟧` tag is refused, the script naming the tag and one bad text inserting none of the batch, regraded and re-signed in `skills/tdd/GRADED` ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 70 | 8 | 16 | 10630 | 219083 | 178121 | 0.57 | 119 | unknown | unknown | unknown |  |  | full |
| a case in `skills/tdd/scripts/tests/py/unit/test_prd_015_prose_signed.py` pins that `prose-owed.sh`, run in-process on the repository root, prints nothing for `skills/tdd/SCRIPTS.md`, and that row SC23 of `skills/tdd/REQUIREMENTS.md` names the refusal of a text already carrying a `⟦criterion k⟧` tag; a small case marked `tree_audit`, no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 10 | 20 | 4002 | 295047 | 34012 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 6 |  |  |
| target | 4 | 5 | 5 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 21 | 42 | 20575 | 546023 | 289136 | 2.32 (estimate) |
