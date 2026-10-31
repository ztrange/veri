### 📊 Metrics — issue 2748

Wall time for the issue: 3155 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2769.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.61 over 29 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87089 tokens, largest 135750 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87089 |
| 2 | $0.07 | 94093 |
| 3 | $0.03 | 95241 |
| 4 | $0.04 | 97326 |
| 5 | $0.03 | 98365 |
| 6 | $0.05 | 102222 |
| 7 | $0.02 | 102572 |
| 8 | $0.02 | 102836 |
| 9 | $0.06 | 107976 |
| 10 | $0.03 | 109499 |
| 11 | $0.06 | 114621 |
| 12 | $0.04 | 116646 |
| 13 | $0.03 | 117554 |
| 14 | $0.04 | 119073 |
| 15 | $0.04 | 121282 |
| 16 | $0.04 | 122925 |
| 17 | $0.05 | 125970 |
| 18 | $0.03 | 126870 |
| 19 | $0.03 | 127689 |
| 20 | $0.03 | 128565 |
| 21 | $0.03 | 129389 |
| 22 | $0.03 | 130163 |
| 23 | $0.04 | 132059 |
| 24 | $0.04 | 133280 |
| 25 | $0.03 | 133958 |
| 26 | $0.03 | 134272 |
| 27 | $0.03 | 134822 |
| 28 | $0.03 | 135038 |
| 29 | $0.03 | 135750 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 3 | 6 | 1459 | 66753 | 37118 | 0.11 |
| red | 7 | 0 | 0 | 0 | 380 | 216 | 69 | 136 | 28713 | 2489710 | 199920 | 1.04 |
| pin | 7 | 7 | 0 | 0 | 293 | 130 | 55 | 110 | 15034 | 1701141 | 128756 | 0.64 |
| diff | 2 | 1 | 0 | 0 | 147 | 24 | 11 | 22 | 2481 | 314913 | 30460 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 9 | 9 | 0 | 0 | 388 | 156 | 63 | 126 | 17801 | 1906736 | 180604 | 0.82 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 448 | 226 | 75 | 148 | 29886 | 2665781 | 215650 | 1.10 |

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
| The develop-red leaf alone is launched with the affected tier: a process case in skills/tdd/scripts/tests/py/test_run_conductor.py launched through run_conductor, launching only this one leaf through the real builder and scripts, no timing or process count, production untouched; breaking that tier in the production prompt or verify.sh reddens it ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 19 | 36 | 6948 | 586217 | 58939 | 0.28 | unknown | unknown | unknown | unknown |  |  | pin |
| The develop-green leaf alone is launched with the fast+affected tier: a process case in skills/tdd/scripts/tests/py/test_run_conductor.py launched through run_conductor, launching only this one leaf through the real builder and scripts, no timing or process count, production untouched; breaking that tier in the production prompt or verify.sh reddens it ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 22 | 44 | 7352 | 757768 | 46393 | 0.27 | unknown | unknown | unknown | unknown |  |  | pin |
| The develop-refactor leaf alone is launched with the affected tier: a process case in skills/tdd/scripts/tests/py/test_run_conductor.py launched through run_conductor, launching only this one leaf through the real builder and scripts, no timing or process count, production untouched; breaking that tier in the production prompt or verify.sh reddens it ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 15 | 30 | 5045 | 507730 | 43576 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| The verify-red leaf alone, given --fast-cmd, is launched with the fast+affected tier: a process case in skills/tdd/scripts/tests/py/test_run_conductor.py launched through run_conductor, launching only this one leaf through the real builder and scripts, no timing or process count, production untouched; breaking that tier in the production prompt or verify.sh reddens it ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 16 | 32 | 5741 | 542434 | 43521 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| The verify-green leaf alone, given --fast-cmd, is launched with the fast+affected tier: a process case in skills/tdd/scripts/tests/py/test_run_conductor.py launched through run_conductor, launching only this one leaf through the real builder and scripts, no timing or process count, production untouched; breaking that tier in the production prompt or verify.sh reddens it ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 20 | 40 | 7780 | 702749 | 47861 | 0.27 | unknown | unknown | unknown | unknown |  |  | pin |
| The verify-refactor leaf alone, given --fast-cmd, is launched with the fast+affected tier: a process case in skills/tdd/scripts/tests/py/test_run_conductor.py launched through run_conductor, launching only this one leaf through the real builder and scripts, no timing or process count, production untouched; breaking that tier in the production prompt or verify.sh reddens it ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 16 | 32 | 5521 | 536716 | 43295 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| The bare verify-refactor leaf alone, with no --fast-cmd, exits 2 and reaches no claude, so no prompt is received: a process case in skills/tdd/scripts/tests/py/test_run_conductor.py launched through run_conductor, launching only this one leaf through the real verify.sh, no timing or process count, production untouched ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 16 | 32 | 5360 | 557237 | 45091 | 0.22 | unknown | unknown | unknown | unknown |  |  | pin |
| The seven-leaf case test_cli_each_phases_leaf_is_launched_with_its_tier_develop_red_and_develop_refactor_affected_verify_red_green_and_refactor_fast_and_affected is removed from skills/tdd/scripts/tests/py/test_run_conductor.py, with nothing else in that file's other cases changed and no production file touched ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 11 | 22 | 2481 | 314913 | 30460 | 0.13 | 224 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 7 | 6 | 7 | 3 | 5 | 5 | 3 | 4 | 7 | 8 | 4 | 23 |  |  |  |  |  |  |  |
| target | 9 | 7 | 6 | 5 | 4 | 5 | 5 | 5 | 5 | 6 | 5 | 6 | 10 | 6 | 7 | 11 | 6 | 4 | 6 |
| fast | 31 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 138 | 274 | 47687 | 4572517 | 396254 | 3.54 (estimate) |
