### 📊 Metrics — issue 1890

Wall time for the issue: 1432 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1966.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 987 | 17463 | 12685 | 0.04 |
| diff | 4 | 2 | 0 | 0 | 343 | 74 | 32 | 62 | 8375 | 978988 | 67850 | 0.35 |
| red | 2 | 0 | 0 | 0 | 48 | 38 | 12 | 20 | 4868 | 316093 | 41151 | 0.18 |
| pin | 2 | 2 | 0 | 0 | 21 | 15 | 6 | 12 | 1719 | 152520 | 28655 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 163 | 54 | 19 | 38 | 5713 | 504875 | 70284 | 0.28 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 259 | 81 | 32 | 58 | 10236 | 960189 | 80057 | 0.40 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| build_develop_prompt.py holds replaces-report, red-contradicted, red-repair, red-missing and red-supersede in `PHASES` itself, `main`'s membership check reads `PHASES` alone, so the usage line and the unknown-phase refusal name every phase `main` accepts; the older cases pinning the old phase list (the `PHASES`/`USAGE` constants of tests/py/unit/test_build_develop_prompt.py and any other verbatim pin of it) are updated in the same commit, and the fast tier and affected suites stay green ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 18 | 34 | 4931 | 586370 | 40432 | 0.21 | 236 | n/a | n/a | n/a |  |  | full |
| a case pins that build-develop-prompt's unknown-phase refusal and its usage line each name every phase `main` accepts, replaces-report, red-contradicted, red-repair, red-missing and red-supersede included (small in-process case, no production change expected) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 9 | 16 | 3402 | 235705 | 35358 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| a case pins that build-develop-prompt's `main` accepts exactly the phases in `PHASES` (each one is never refused as unknown, a name outside it is) and that `WANT`'s keys are exactly `PHASES` (small in-process case, no production change expected) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 9 | 16 | 3185 | 232908 | 34448 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| skills/tdd/SCRIPTS.md's build-develop-prompt.sh entry lists the same phases `PHASES` holds, replaces-report, red-contradicted, red-supersede and the interface phases included; no case ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 14 | 28 | 3444 | 392618 | 27418 | 0.14 | 159 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 5 | 5 | 6 | 6 | 6 | 6 | 6 |  |
| affected | 42 | 41 | 43 | 2 | 1 | 0 | 41 | 0 |
| target | 1 | 0 | 0 | 0 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 51 | 96 | 15949 | 1465064 | 150341 | 0.68 |
