### 📊 Metrics — issue 1507

Wall time for the issue: 1647 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1576.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 11 | 1 | 2 | 1177 | 12193 | 43365 | 0.19 |
| red | 5 | 1 | 0 | 0 | 358 | 143 | 37 | 74 | 15600 | 2050733 | 270390 | 1.44 |
| green | 2 | 1 | 0 | 0 | 228 | 48 | 14 | 28 | 4889 | 728687 | 97095 | 0.51 |
| refactor | 2 | 1 | 0 | 0 | 107 | 24 | 8 | 16 | 2004 | 354747 | 90767 | 0.42 |
| pin | 3 | 3 | 0 | 0 | 78 | 56 | 16 | 30 | 5116 | 702149 | 138161 | 0.67 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 317 | 122 | 32 | 62 | 11409 | 1426138 | 319214 | 1.53 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 470 | 160 | 44 | 88 | 17377 | 2422371 | 320564 | 1.70 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| On a ⟦replaces-case⟧ step, when the green verifier leaf answers VERDICT: PASS and a case the --step text names is still in its suite, verify.sh green exits 1 (REJECT) with a stdout reason naming each surviving case, whatever the leaf's REASON said; the survivors check runs after the leaf and adds no verifier parameter. Pinned in tests/py/test_verify.py by a stub PASS leaf on a step naming two cases, one still present in the scratch suite ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 110 | 34 | 68 | 11284 | 1716845 | 295004 | 1.46 | 482 | unknown | 0/5 | nothing-left |  |  | full |
| On a ⟦replaces-case⟧ step, when the green verifier leaf answers VERDICT: PASS and the named-cases check cannot answer (its exit 2, e.g. an unreadable suite), verify.sh green exits 2 ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 69 | 16 | 30 | 7010 | 814436 | 102631 | 0.56 | unknown | unknown | unknown | unknown |  |  | pin |
| A green verify on a step without ⟦replaces-case⟧ returns the leaf's verdict unchanged (a stub PASS leaf exits 0 even though no named-cases check applies) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 13 | 26 | 4919 | 682403 | 99843 | 0.52 | unknown | unknown | unknown | unknown |  |  | pin |
| A green verify on a ⟦replaces-case⟧ step whose every named case is gone from its suite, with a stub PASS leaf, still exits 0 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 12 | 24 | 4396 | 622632 | 98935 | 0.50 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| On a ⟦replaces-case⟧ step, when the green verifier leaf answers VERDICT: PASS and a case the --step text names is still in its suite, verify.sh green exits 1 (REJECT) with a stdout reason naming each surviving case, whatever the leaf's REASON said; the survivors check runs after the leaf and adds no verifier parameter. Pinned in tests/py/test_verify.py by a stub PASS leaf on a step naming two cases, one still present in the scratch suite ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 107 | 0.42 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 21 | 1 | 21 | 22 | 20 | 21 |  |
| fast | 53 | 56 | 55 |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 2 | 1 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 76 | 150 | 28786 | 3848509 | 639778 | 3.23 |
