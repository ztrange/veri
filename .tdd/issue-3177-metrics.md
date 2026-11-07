### 📊 Metrics — issue 3177

Wall time for the issue: 1248 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3211.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 1062 | 0 | 23815 | 0.07 |
| skill-edit | 2 | 0 | 0 | 0 | 90 | 77 | 13 | 24 | 9578 | 305522 | 71941 | 0.31 |
| prose | 7 | 0 | 0 | 0 | 121 | 105 | 7 | 14 | 15126 | 24655 | 89250 | 0.38 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 1 | 1 | 0 | 0 | 11 | 8 | 1 | 2 | 1062 | 0 | 23815 | 0.07 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skills/tdd/PREFLIGHT-FAILURES.md is created holding every preflight failure branch (each sentence of PREFLIGHT.md that stops or bails the run), signed against its new `## skills/tdd/PREFLIGHT-FAILURES.md` requirements list (PF20, PF21, PF30, PF32, PF36, CY117, PF40–PF58) ⟦skill-edit⟧ ⟦criterion 1⟧ | 2 | 0 | 0 | 0 | 0 | 0 | 41 | 6 | 12 | 5193 | 77016 | 41182 | 0.16 | 74 | unknown | unknown | unknown |  |  | full |
| skills/tdd/PREFLIGHT.md carries only what a preflight that passes needs, its failure branches removed and replaced by a pointer sentence sending a refused check to `<base directory>/PREFLIGHT-FAILURES.md`, read then and not before (PF59), its list losing the moved rows; pins updated in skills/tdd/scripts/tests/py/test_prose_owed_process.py, skills/tdd/scripts/tests/py/unit/test_skill_resume_pointers.py, skills/tdd/scripts/tests/py/test_skill_preflight.py ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 103 | 12 | 22 | 13782 | 250129 | 92505 | 0.39 | 147 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 21 | 40 | 25766 | 330177 | 185006 | 0.75 |
