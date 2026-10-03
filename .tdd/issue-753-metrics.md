### 📊 Metrics — issue 753

Wall time for the issue: 7547 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/773.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 2 | 4 | 1225 | 59946 | 39472 | 0.35 |
| red | 9 | 4 | 0 | 0 | 939 | 425 | 97 | 192 | 39366 | 5606737 | 504084 | 5.94 |
| pin | 1 | 1 | 0 | 0 | 194 | 18 | 5 | 10 | 1900 | 209849 | 40295 | 0.40 |
| green | 8 | 4 | 0 | 0 | 3749 | 518 | 123 | 240 | 47169 | 6791338 | 417822 | 5.65 |
| refactor | 8 | 4 | 0 | 0 | 932 | 163 | 39 | 78 | 15184 | 1682920 | 351083 | 3.45 |
| predicate | 2 | 0 | 0 | 0 | 48 | 36 | 7 | 14 | 3620 | 269322 | 79629 | 0.76 |
| structural | 2 | 0 | 0 | 0 | 176 | 32 | 8 | 16 | 2789 | 320685 | 77889 | 0.74 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 14 | 14 | 0 | 0 | 3292 | 447 | 105 | 210 | 41240 | 4932039 | 620143 | 6.77 |
| developer | claude-opus-5-5 | 17 | 0 | 0 | 0 | 2762 | 757 | 176 | 344 | 70013 | 10008758 | 890131 | 10.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 48 | 0.76 |
| structural | 0 | 0.00 | 176 | 0.74 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| verify.sh given `--step ""`, or a trailing `--step` with no value, exits 2, names `--step` on stderr and launches no verifier leaf ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 98 | 17 | 34 | 7880 | 871889 | 94637 | 1.09 | unknown | unknown | unknown | unknown |  |  | pin |
| a `verdict-<phase>` supervision of run-verdict.sh whose verify.sh refused its arguments with exit 2 records 2 in `.tdd/verdict-<phase>.exit` and exits 2, never 1, so the conductor's wait never reads a bad argument as a REJECT ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 282 | 66 | 128 | 24432 | 3505501 | 305329 | 3.63 | 929 | unknown | 0/5 | nothing-structural |  |  | full |
| SKILL.md's verify-rebase launch line passes a `--step` that falls back to the last done step's text (`ledger-steps.sh last-done`) when `ledger-steps.sh current` prints nothing ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 293 | 65 | 130 | 25047 | 3669539 | 309441 | 3.71 | 1443 | unknown | 0/5 | nothing-structural |  |  | full |
| SKILL.md's structural pass spells the transform verifier's launch line, and its `--step` falls back to the last done step's text when no step is open ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 278 | 69 | 134 | 28943 | 3919894 | 325400 | 3.97 | 2028 | unknown | 0/5 | structural-owed |  |  | full |
| SKILL.md's general verifier launch shape and the revise loop's re-verify line fall back to the last done step's text when no step is open, so an end-of-run verifier launches first time ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 173 | 47 | 94 | 17317 | 2324021 | 278477 | 3.04 | 1292 | unknown | 0/5 | structural-owed |  |  | full |
| `make test` is green ⟦full-suite⟧ ⟦criterion 3⟧ | 4 | 0 | 0 | 0 | 0 | 0 | 68 | 15 | 30 | 6409 | 590007 | 157518 | 1.51 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| a `verdict-<phase>` supervision of run-verdict.sh whose verify.sh refused its arguments with exit 2 records 2 in `.tdd/verdict-<phase>.exit` and exits 2, never 1, so the conductor's wait never reads a bad argument as a REJECT ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 188 | 0.82 |
| SKILL.md's verify-rebase launch line passes a `--step` that falls back to the last done step's text (`ledger-steps.sh last-done`) when `ledger-steps.sh current` prints nothing ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 135 | 0.87 |
| SKILL.md's structural pass spells the transform verifier's launch line, and its `--step` falls back to the last done step's text when no step is open ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 318 | 0.91 |
| SKILL.md's general verifier launch shape and the revise loop's re-verify line fall back to the last done step's text when no step is open, so an end-of-run verifier launches first time ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 291 | 0.85 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 85 | 1 | 1 | 1 | 0 | 127 | 54 | 0 | 1 | 58 | 39 | 39 | 171 | 173 | 0 | 201 | 37 | 37 | 45 | 197 | 256 | 0 | 225 | 42 | 43 | 0 | 178 | 213 | 207 | 1 | 131 |
| target | 85 | 85 | 2 | 37 | 37 | 51 | 43 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 46 | 45 | 41 | 41 | 37 | 40 | 37 | 35 | 40 | 49 | 40 | 39 | 40 | 36 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 281 | 554 | 111253 | 14940797 | 1510274 | 17.30 |
