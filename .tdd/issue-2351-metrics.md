### 📊 Metrics — issue 2351

Wall time for the issue: 1333 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2398.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.59 over 37 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87648 tokens, largest 120106 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87648 |
| 2 | $0.03 | 89665 |
| 3 | $0.03 | 91554 |
| 4 | $0.02 | 91859 |
| 5 | $0.02 | 92281 |
| 6 | $0.02 | 92647 |
| 7 | $0.02 | 93003 |
| 8 | $0.02 | 93600 |
| 9 | $0.03 | 94651 |
| 10 | $0.04 | 97756 |
| 11 | $0.03 | 98901 |
| 12 | $0.03 | 100173 |
| 13 | $0.02 | 100589 |
| 14 | $0.03 | 101545 |
| 15 | $0.02 | 102090 |
| 16 | $0.03 | 103746 |
| 17 | $0.02 | 104253 |
| 18 | $0.03 | 105169 |
| 19 | $0.03 | 105789 |
| 20 | $0.03 | 106362 |
| 21 | $0.03 | 107049 |
| 22 | $0.03 | 107613 |
| 23 | $0.04 | 109724 |
| 24 | $0.03 | 110407 |
| 25 | $0.03 | 111236 |
| 26 | $0.03 | 112249 |
| 27 | $0.03 | 112892 |
| 28 | $0.04 | 115315 |
| 29 | $0.03 | 116021 |
| 30 | $0.03 | 116318 |
| 31 | $0.03 | 117370 |
| 32 | $0.03 | 117667 |
| 33 | $0.03 | 118001 |
| 34 | $0.03 | 118757 |
| 35 | $0.03 | 119186 |
| 36 | $0.03 | 119545 |
| 37 | $0.03 | 120106 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 7 | 2 | 4 | 853 | 31632 | 33055 | 0.09 |
| prose | 5 | 0 | 0 | 0 | 51 | 39 | 5 | 10 | 5775 | 15117 | 41931 | 0.16 |
| skill-edit | 1 | 0 | 0 | 0 | 12 | 10 | 3 | 6 | 814 | 58493 | 30256 | 0.09 |
| diff | 2 | 1 | 0 | 0 | 400 | 39 | 15 | 30 | 3515 | 407951 | 45014 | 0.19 |
| red | 1 | 0 | 0 | 0 | 24 | 17 | 6 | 12 | 2115 | 191903 | 19379 | 0.09 |
| pin | 1 | 1 | 0 | 0 | 20 | 12 | 4 | 8 | 1136 | 109371 | 15942 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 228 | 37 | 12 | 24 | 3548 | 289305 | 79893 | 0.26 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 226 | 38 | 15 | 30 | 4071 | 451552 | 33497 | 0.17 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Add B10 to `skills/veri-bail/REQUIREMENTS.md` under `## skills/veri-bail/SKILL.md`, exactly as the issue's table row gives it, edit *Budgets and ledger* in `skills/veri-bail/SKILL.md` so the unit grades PASS against its whole list, and sign it in `skills/veri-bail/GRADED` (unit `skills/veri-bail/SKILL.md`) ⟦skill-edit⟧ ⟦criterion 3⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 38 | 7 | 14 | 4944 | 72961 | 60890 | 0.21 | 85 | unknown | unknown | unknown |  |  | full |
| The branch's diff shows veri-bail's *Budgets and ledger* section stating that a ledger step amended in place between runs is committed with a `plan: rewrite` subject, so it becomes the growth baseline `ledger-growth.sh plan-sha` reads; this step changes no file, the edit having landed in the skill-edit step ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 15 | 30 | 3515 | 407951 | 45014 | 0.19 | 461 | n/a | n/a | n/a |  |  | full |
| A resumed run whose ledger step was reworded in place in a `plan: rewrite` commit passes the growth check: `ledger-growth.sh plan-sha` names that rewrite commit, and `ledger-growth.sh` run against the ledger as that commit holds it exits 0 naming no line, so it does not bail `step-added-off-route` on that step (a small unit case in `skills/tdd/scripts/tests/py/unit/test_ledger_growth.py`, no production change) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 10 | 20 | 3251 | 301274 | 35321 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast | 17 | 16 |  |  |  |
| affected | 0 | 161 | 0 | 159 | 1 |
| target | 2 | 2 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 35 | 70 | 14208 | 814467 | 185577 | 0.69 |
