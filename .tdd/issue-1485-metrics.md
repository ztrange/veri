### 📊 Metrics — issue 1485

Wall time for the issue: 8641 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 12 of 13 planned.
Outcome: the run bailed — rebased-tip-red, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 15 | 1 | 2 | 1927 | 12193 | 45227 | 0.20 |
| red | 21 | 9 | 0 | 0 | 736 | 396 | 114 | 226 | 47834 | 5868852 | 1078409 | 5.38 |
| green | 20 | 9 | 1 | 0 | 4740 | 433 | 145 | 276 | 45737 | 7381671 | 967305 | 5.31 |
| refactor | 18 | 9 | 0 | 0 | 1231 | 168 | 67 | 130 | 16853 | 2896942 | 853091 | 3.87 |
| pin | 3 | 3 | 0 | 0 | 75 | 30 | 10 | 20 | 3562 | 436566 | 140758 | 0.64 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 32 | 31 | 1 | 0 | 3544 | 477 | 157 | 306 | 52149 | 7410119 | 1489318 | 7.22 |
| developer | claude-sonnet-5-5 | 29 | 0 | 0 | 0 | 2771 | 478 | 157 | 304 | 56775 | 7865837 | 1484024 | 7.29 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 487 | 87 | 23 | 44 | 6989 | 1320268 | 111448 | 0.89 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 937 | 1.34 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| With no model variable set, leaf-model.sh prints sonnet and exits 0 for develop-red, develop-rebase, develop-reconcile, develop-over-budget and verify-green, and opus for revise-green-2 and develop-exhausted; a role variable still beats VERI_MODEL, VERI_MODEL_REVISE still beats VERI_MODEL_DEVELOPER for the redo leaves, and VERI_MODEL beats every default ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 198 | 56 | 110 | 18997 | 3026791 | 384190 | 2.28 | 1259 | 1/2 | 0/5 | nothing-structural |  |  | full |
| With no model variable set, the claude command line of a supervised leaf carries --model sonnet for develop-red and verify-green, and --model opus for revise-green-2 and develop-exhausted ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 10 | 20 | 4340 | 504831 | 98596 | 0.49 | unknown | unknown | unknown | unknown |  |  | pin |
| With no model variable set, run-conductor.sh <issue> launches claude with --model opus ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 93 | 34 | 64 | 10734 | 1622480 | 292470 | 1.44 | 992 | unknown | 0/5 | nothing-structural |  |  | full |
| With no model variable set, in the same .tdd/ directory, a verify-green REJECT is followed by revise-green-1 carrying --model opus, then the next step's develop-red and the same step's develop-refactor each carry --model sonnet ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 10 | 20 | 4404 | 503646 | 99327 | 0.49 | unknown | unknown | unknown | unknown |  |  | pin |
| Each of VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE set to "" or to whitespace only gives the same model and exit 0 as when unset, for develop-red, revise-green, revise-green-2, develop-exhausted and verify-green (preflight's three leaf-model.sh calls included); a value with internal whitespace (sonnet 5) still exits 2 with nothing on stdout ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 103 | 33 | 64 | 11925 | 1615208 | 293762 | 1.46 | 636 | unknown | 0/5 | structural-owed |  |  | full |
| SKILL.md's preflight step 6 says an empty or whitespace-only model variable is treated as unset and that only a value with internal whitespace stops the run ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 33 | 62 | 10315 | 1584284 | 296209 | 1.45 | 1391 | unknown | 0/5 | nothing-left |  |  | full |
| With VERIFY_LEAF_ARGS carrying --model x and no model variable set, verify.sh does not exit 2 and the verifier leaf's command line names model x ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 97 | 36 | 66 | 11369 | 1669339 | 300434 | 1.48 | 863 | unknown | 0/5 | nothing-structural |  |  | full |
| With VERIFY_LEAF_ARGS carrying --model x and VERI_MODEL_VERIFIER also set, verify.sh still exits 2 ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 12 | 24 | 5195 | 651400 | 102840 | 0.53 | unknown | unknown | unknown | unknown |  |  | pin |
| model-knobs-recorded.test.sh goes red, naming the document, when SKILL.md's supervise.sh bullet or CLAUDE.md's model-knob invariant stops naming VERI_MODEL_REVISE ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 96 | 29 | 58 | 10760 | 1450203 | 300600 | 1.46 | 367 | unknown | 0/5 | structural-owed |  |  | full |
| CLAUDE.md's model-knob invariant and SKILL.md's supervise.sh bullet state the shipped defaults (sonnet for first tries and verifiers, opus for redo leaves and the conductor) instead of no --model ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 96 | 28 | 56 | 10360 | 1385272 | 301044 | 1.45 | 730 | unknown | 0/5 | nothing-structural |  |  | full |
| supervise.sh's Tunables (env) header names all four model knobs and the shipped defaults instead of no --model ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 69 | 25 | 50 | 7481 | 1167437 | 286826 | 1.34 | 392 | unknown | 0/5 | nothing-left |  |  | full |
| The metrics footer's sentence on when dollars are comparable names VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 75 | 30 | 58 | 8106 | 1403140 | 283265 | 1.35 | 341 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With no model variable set, leaf-model.sh prints sonnet and exits 0 for develop-red, develop-rebase, develop-reconcile, develop-over-budget and verify-green, and opus for revise-green-2 and develop-exhausted; a role variable still beats VERI_MODEL, VERI_MODEL_REVISE still beats VERI_MODEL_DEVELOPER for the redo leaves, and VERI_MODEL beats every default ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 178 | 0.46 |
| With no model variable set, run-conductor.sh <issue> launches claude with --model opus ⟦criterion 1⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 255 | 0.44 |
| Each of VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE set to "" or to whitespace only gives the same model and exit 0 as when unset, for develop-red, revise-green, revise-green-2, develop-exhausted and verify-green (preflight's three leaf-model.sh calls included); a value with internal whitespace (sonnet 5) still exits 2 with nothing on stdout ⟦criterion 3⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 94 | 0.43 |
| SKILL.md's preflight step 6 says an empty or whitespace-only model variable is treated as unset and that only a value with internal whitespace stops the run ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 87 | 0.41 |
| With VERIFY_LEAF_ARGS carrying --model x and no model variable set, verify.sh does not exit 2 and the verifier leaf's command line names model x ⟦criterion 4⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 267 | 0.45 |
| model-knobs-recorded.test.sh goes red, naming the document, when SKILL.md's supervise.sh bullet or CLAUDE.md's model-knob invariant stops naming VERI_MODEL_REVISE ⟦criterion 5⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 82 | 0.42 |
| CLAUDE.md's model-knob invariant and SKILL.md's supervise.sh bullet state the shipped defaults (sonnet for first tries and verifiers, opus for redo leaves and the conductor) instead of no --model ⟦criterion 5⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 88 | 0.43 |
| supervise.sh's Tunables (env) header names all four model knobs and the shipped defaults instead of no --model ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 88 | 0.41 |
| The metrics footer's sentence on when dollars are comparable names VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 92 | 0.43 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 24 | 194 | 26 | 21 | 77 | 2 | 23 | 1 | 0 | 170 | 163 | 164 | 1 | 27 | 2 | 1 | 2 | 2 | 2 | 1 | 357 | 335 | 1 | 22 | 182 | 1 | 49 | 0 | 174 | 21 | 3 | 4 | 3 | 3 | 4 | 5 | 355 | 0 | 0 | 4 | 4 | 4 | 24 | 5 | 20 | 2 | 2 | 1 | 1 | 1 | 1 | 0 | 3 |
| fast | 62 | 61 | 59 | 62 | 64 | 67 | 65 | 64 | 64 | 62 | 60 | 68 | 62 | 62 | 63 | 63 | 62 | 58 | 57 | 58 | 58 | 60 | 63 | 61 | 61 | 61 | 62 | 59 | 61 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 5 | 7 | 1 | 6 | 5 | 6 | 0 | 2 | 2 | 1 | 1 | 3 | 4 | 4 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 337 | 654 | 115913 | 16596224 | 3084790 | 15.41 |
