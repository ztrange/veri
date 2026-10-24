### 📊 Metrics — issue 1828

Wall time for the issue: 531 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2298.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.41 over 30 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90097 |
| 2 | $0.02 | 90412 |
| 3 | $0.02 | 91135 |
| 4 | $0.03 | 92425 |
| 5 | $0.03 | 94321 |
| 6 | $0.02 | 94700 |
| 7 | $0.02 | 95029 |
| 8 | $0.02 | 95350 |
| 9 | $0.02 | 95909 |
| 10 | $0.03 | 96690 |
| 11 | $0.03 | 98005 |
| 12 | $0.08 | 106003 |
| 13 | $0.03 | 107005 |
| 14 | $0.03 | 108576 |
| 15 | $0.03 | 109014 |
| 16 | $0.02 | 109282 |
| 17 | $0.03 | 110155 |
| 18 | $0.02 | 110506 |
| 19 | $0.03 | 111194 |
| 20 | $0.03 | 111778 |
| 21 | $0.03 | 112486 |
| 22 | $0.03 | 112946 |
| 23 | $0.03 | 113288 |
| 24 | $0.03 | 113821 |
| 25 | $0.03 | 114630 |
| 26 | $0.03 | 115300 |
| 27 | $0.03 | 115574 |
| 28 | $0.03 | 116129 |
| 29 | $0.03 | 116654 |
| 30 | $0.03 | 117069 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 6 | 2 | 4 | 745 | 48330 | 14707 | 0.05 |
| prose | 2 | 0 | 0 | 0 | 162 | 159 | 2 | 4 | 27268 | 2032 | 197260 | 0.77 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 1 | 1 | 0 | 0 | 8 | 6 | 2 | 4 | 745 | 48330 | 14707 | 0.05 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skill-edit step for the unit `skills/tdd/SKILL.md`: the #1730 plan-pin rule (a `⟦diff-checked⟧` step for the text and a separate step for the case pinning it, both tagged with the same `⟦criterion k⟧`, the case's step after the text's) has its row in `skills/tdd/REQUIREMENTS.md` under `## skills/tdd/SKILL.md`, the unit is graded by `grade-prose.sh` against that list and signed, so `GRADED` carries a line for the unit whose signature matches its current text and `prose-owed.sh` prints nothing for it ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 86 | 1 | 2 | 14853 | 649 | 98999 | 0.40 | 111 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier |
| --- |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 4 | 8 | 28013 | 50362 | 211967 | 0.82 |
