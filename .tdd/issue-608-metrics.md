### 📊 Metrics — issue 608

Wall time for the issue: 3869 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/614.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 7 | 1 | 2 | 917 | 24071 | 21759 | 0.10 |
| red | 9 | 3 | 0 | 0 | 520 | 285 | 62 | 116 | 33003 | 2863907 | 306190 | 2.13 |
| green | 6 | 3 | 0 | 0 | 1421 | 345 | 47 | 88 | 19580 | 2112660 | 154276 | 2.12 |
| refactor | 6 | 3 | 0 | 0 | 198 | 77 | 29 | 54 | 8443 | 1165442 | 152248 | 0.93 |
| pin | 3 | 2 | 1 | 0 | 280 | 85 | 25 | 48 | 9282 | 1160304 | 74461 | 0.62 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 116 | 0.39 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| hermetic-suites.test.sh's conductor-lock cases each run a slice of solvable-issues.test.sh, the way the label-band case does, and none runs a whole copy of it ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 174 | 42 | 80 | 19767 | 1914288 | 188685 | 1.34 | 452 | unknown | 1/5 | nothing-left |  |  | full |
| hermetic-suites.test.sh pins that a live conductor lock on every fixture issue number in the surrounding repository changes neither the exit code nor the stdout of solvable-issues.sh, and goes red when solvable-issues.sh starts reading that lock ⟦criterion 1⟧ | 4 | 1 | 1 | 0 | 0 | 0 | 131 | 33 | 62 | 14446 | 1569552 | 119953 | 0.94 | unknown | 1/2 | unknown | unknown |  |  | pin |
| skill-leaf-env.test.sh launches each launch line in SKILL.md at most once per ledger shape it plants ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 315 | 41 | 76 | 16517 | 1799339 | 156333 | 2.04 | 1395 | unknown | 1/5 | nothing-left |  |  | full |
| skill-leaf-env.test.sh pins, for every launch line in SKILL.md, the environment each leaf launch receives, VERI_STEP included, and goes red when one launch line drops a variable it pins ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 77 | 19 | 36 | 9219 | 916558 | 71543 | 0.56 | unknown | unknown | unknown | unknown |  |  | pin |
| repair the red full suite: no-job-spec-kills.test.sh fails — "no file under skills/ ends a background process by a job spec" names skill-leaf-env.test.sh:37 and :442, whose step-title text spells `kill %1`, and "every exemption names a line … that ends a background process by a job spec" says the [skill-leaf-env.test.sh:395] exemption excuses nothing — no-job-spec-kills.test.sh is green again with every assertion it makes kept ⟦added⟧ ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 95 | 28 | 52 | 10359 | 1102576 | 150661 | 0.93 | 306 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| hermetic-suites.test.sh's conductor-lock cases each run a slice of solvable-issues.test.sh, the way the label-band case does, and none runs a whole copy of it ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 66 | 0.32 |
| skill-leaf-env.test.sh launches each launch line in SKILL.md at most once per ledger shape it plants ⟦criterion 4⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 84 | 0.35 |
| repair the red full suite: no-job-spec-kills.test.sh fails — "no file under skills/ ends a background process by a job spec" names skill-leaf-env.test.sh:37 and :442, whose step-title text spells `kill %1`, and "every exemption names a line … that ends a background process by a job spec" says the [skill-leaf-env.test.sh:395] exemption excuses nothing — no-job-spec-kills.test.sh is green again with every assertion it makes kept ⟦added⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 48 | 0.26 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 20 | 0 | 22 | 11 | 13 | 0 | 19 | 0 | 18 | 19 | 0 | 18 | 19 | 0 | 18 | 18 | 18 |  |  |
| fast | 5 | 5 | 4 | 5 | 5 | 4 | 4 | 5 | 5 |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 13 | 0 | 0 | 10 | 13 | 0 | 14 | 14 | 0 | 18 | 17 | 18 | 19 | 18 | 18 | 18 | 18 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 164 | 308 | 71225 | 7326384 | 708934 | 5.90 |
