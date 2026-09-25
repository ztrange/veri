### 📊 Metrics — issue 437

Wall time for the issue: 16180 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 9 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/466.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 14 | 2 | 4 | 1246 | 56009 | 37265 | 0.33 |
| red | 18 | 8 | 0 | 0 | 2020 | 1231 | 210 | 406 | 114672 | 12461470 | 1089616 | 13.50 |
| green | 26 | 8 | 5 | 0 | 9708 | 2159 | 423 | 834 | 198915 | 25642922 | 1505001 | 21.15 |
| refactor | 15 | 7 | 0 | 0 | 2825 | 786 | 158 | 312 | 77207 | 8244904 | 729474 | 9.03 |
| pin | 2 | 2 | 0 | 0 | 122 | 65 | 14 | 26 | 6498 | 581521 | 90439 | 0.97 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 12750 | 25.76 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A step title containing a dollar sign, a backtick and a double quote reaches a developer leaf launched by SKILL.md's documented launch line byte-identical in its VERI_STEP environment ⟦criterion 1⟧ | 15 | 5 | 2 | 0 | 0 | 0 | 928 | 191 | 368 | 87946 | 10213994 | 800510 | 10.21 | 4340 | 2/2 | 2/5 | nothing-structural |
| The rule SKILL.md states once for how a step title reaches a command line says it reaches it as data, not in hand-typed double quotes, and no longer contradicts the launch lines ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 266 | 57 | 112 | 22737 | 2803410 | 285111 | 3.30 | 513 | unknown | 1/5 | structural-owed |
| A step title containing a dollar sign, a backtick and a double quote reaches a verifier launched by SKILL.md's documented verdict launch line byte-identical, both in its VERI_STEP environment and in its --step argument ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 341 | 76 | 148 | 32379 | 4184622 | 315321 | 4.01 | 1245 | unknown | 1/5 | structural-owed |
| Every other developer and verifier launch line in SKILL.md that carries the step title, develop-green, revise, develop-exhausted, develop-reconcile, verify-pin, verify-green, verify-refactor and the general launch forms under Launching a leaf, delivers a title with a dollar sign, a backtick and a double quote byte-identical ⟦added⟧ ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 633 | 127 | 250 | 61128 | 7875850 | 484638 | 6.68 | 2715 | 1/2 | 1/5 | structural-owed |
| The conductor's own title-carrying command lines in SKILL.md, the event.sh marks and preserve-attempt.sh calls and the title fragments handed to tick-ledger.sh, clear-refactor-pending.sh and tick-issue-criterion.sh, pass a title with a dollar sign, a backtick and a double quote through byte-identical | 10 | 3 | 2 | 0 | 0 | 0 | 1064 | 161 | 318 | 98094 | 10701050 | 640936 | 9.23 | 3639 | 2/2 | 2/5 | structural-owed |
| The prompt SKILL.md builds with build-develop-prompt.sh for every developer phase, and the anchor it hands add-ledger-step.sh, carry a step title with a dollar sign, a backtick and a double quote byte-identical ⟦added⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 477 | 92 | 184 | 44598 | 5695364 | 367892 | 4.97 | 1659 | unknown | 3/5 | structural-owed |
| The pin probes with one title carrying all three characters at once and goes red when a launch line is put back to the hand-typed double-quoted form of #431 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 133 | 25 | 48 | 13148 | 1581030 | 124062 | 1.57 | unknown | unknown | unknown | unknown |
| The #431 guard in skill-leaf-launch.test.sh still refuses a single-quoted step title and its exemption table still holds over the rewritten document ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 116 | 18 | 34 | 11093 | 914120 | 107766 | 1.27 | unknown | unknown | unknown | unknown |
| Repair: make test is green with both the step-8 #431 guard pin in skill-leaf-launch.test.sh and verifier-launch-guard.test.sh's planted single-quoted title, which today fails the pin because the plant leaves no double-quoted fenced line carrying the step title ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 283 | 58 | 116 | 26169 | 2961377 | 288294 | 3.42 | 1015 | unknown | 2/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s | run 65 s | run 66 s | run 67 s | run 68 s | run 69 s | run 70 s | run 71 s | run 72 s | run 73 s | run 74 s | run 75 s | run 76 s | run 77 s | run 78 s | run 79 s | run 80 s | run 81 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 17 | 17 | 0 | 82 | 81 | 83 | 17 | 0 | 17 | 63 | 0 | 84 | 0 | 83 | 81 | 17 | 1 | 0 | 1 | 62 | 0 | 0 | 9 | 65 | 1 | 0 | 1 | 18 | 17 | 0 | 64 | 64 | 0 | 82 | 18 | 17 | 17 | 19 | 18 | 0 | 69 | 69 | 83 | 87 | 1 | 21 | 20 | 20 | 22 | 24 | 70 | 91 | 0 | 89 | 0 | 22 | 21 | 0 | 22 | 23 | 23 | 0 | 90 | 91 | 90 | 22 | 23 | 23 | 23 | 22 | 23 | 22 | 23 | 0 | 3 | 2 | 3 | 4 | 4 | 3 | 4 |
| target | 16 | 16 | 19 | 0 | 17 | 17 | 17 | 0 | 17 | 16 | 0 | 19 | 20 | 19 | 19 | 19 | 22 | 21 | 22 | 22 | 23 | 23 | 22 | 1 | 1 | 0 | 1 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 289 | 293 | 292 | 287 | 289 | 291 | 292 | 296 | 290 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 3 | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 294 | 296 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 807 | 1582 | 398538 | 46986826 | 3451795 | 44.99 |
