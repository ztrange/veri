### 📊 Metrics — issue 2000

Wall time for the issue: 889 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2050.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 2 | 4 | 945 | 29440 | 30500 | 0.09 |
| red | 2 | 0 | 0 | 0 | 104 | 91 | 20 | 40 | 6715 | 630107 | 58960 | 0.28 |
| pin | 2 | 2 | 0 | 0 | 29 | 21 | 8 | 16 | 2095 | 202341 | 24293 | 0.10 |
| diff | 2 | 1 | 0 | 0 | 47 | 27 | 8 | 16 | 1630 | 199599 | 21868 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 57 | 37 | 13 | 26 | 3691 | 302647 | 65820 | 0.23 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 134 | 111 | 25 | 50 | 7694 | 758840 | 69801 | 0.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `skills/tdd/scripts/tests/py/unit/test_emitted_text.py` pins the rendered text of `build-develop-prompt.sh red-repair` with one checksum row in its PROMPTS table, in the same form as the existing `build-develop-prompt.sh red` row, so that changing one word in `develop-red-repair.md` (for example "Leave no change" to "Leave any change" at line 78) fails that row; test-only, no prompt or script change, and every existing case keeps its name and outcome ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 13 | 26 | 4186 | 371713 | 50622 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| `skills/tdd/scripts/tests/py/unit/test_emitted_text.py` pins the rendered text of `build-develop-prompt.sh red-contradicted` with one checksum row in its PROMPTS table, in the same form as the existing `build-develop-prompt.sh red` row, so that changing one word in `develop-red-contradicted.md` fails that row; test-only, no prompt or script change, and every existing case keeps its name and outcome ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 15 | 30 | 4624 | 460735 | 32631 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| The branch's diff is test-only: no file under `skills/tdd/scripts/prompts/` and no script or module under `skills/tdd/scripts/` outside `tests/` changes, and every existing case keeps its name and outcome ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 8 | 16 | 1630 | 199599 | 21868 | 0.09 | 81 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 |
| target | 0 | 1 | 1 | 1 |
| fast | 6 | 6 |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 38 | 76 | 11385 | 1061487 | 135621 | 0.56 |
