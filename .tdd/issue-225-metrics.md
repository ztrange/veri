### 📊 Metrics — issue 225

Wall time for the issue: 425 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 9 planned.
Outcome: the run bailed — untestable-criterion, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 49 | 41 | 5 | 10 | 3661 | 153143 | 72472 | 0.68 |
| red | 15 | 4 | 1 | 0 | 1340 | 635 | 118 | 232 | 59070 | 5687357 | 704972 | 7.96 |
| green | 10 | 4 | 1 | 0 | 938 | 341 | 85 | 168 | 33292 | 3990435 | 405504 | 4.71 |
| refactor | 8 | 4 | 0 | 0 | 331 | 257 | 60 | 118 | 24863 | 2824334 | 353580 | 3.89 |
| pin | 3 | 3 | 0 | 0 | 96 | 75 | 15 | 30 | 7046 | 606998 | 118636 | 1.21 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 799 | 2.00 | 55 | 0.88 |
| green | 578 | 1.84 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| A shared helper file under skills/tdd/scripts/tests/, not named *.test.sh and not picked up by make test's suite glob, when sourced defines report and plain with the same behaviour as the copies in the four *-recorded.test.sh suites that carry them ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 197 | 43 | 86 | 18252 | 2012031 | 259427 | 2.84 | 377 | unknown | 0/5 | nothing-left |
| The shared helper file, when sourced, also defines records, bullet and says with the same behaviour as the copies in selection-order-recorded.test.sh and model-knobs-recorded.test.sh ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 298 | 67 | 134 | 29099 | 3114516 | 343562 | 3.95 | 1060 | 1/2 | 2/5 | structural-owed |
| selection-order-recorded.test.sh and model-knobs-recorded.test.sh source the shared file and define no report, plain, records, bullet or says of their own ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 281 | 59 | 118 | 26652 | 2839592 | 334656 | 3.78 | 810 | 1/2 | 0/5 | nothing-left |
| lane-rule-recorded.test.sh and unit-tier-recorded.test.sh source the shared file and define no report or plain of their own, while each keeps its own different says ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 235 | 54 | 104 | 22190 | 2590631 | 274429 | 3.16 | 394 | unknown | 3/5 | structural-owed |
| Each of the four suites still runs standalone as bash <suite> from any working directory and its output still ends in its own <n> passed, <m> failed count line ⟦criterion 2⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 32 | 5 | 10 | 2574 | 221360 | 53142 | 0.52 | unknown | unknown | unknown | unknown |
| The shared file sourced from a working directory other than the repo root defines report, plain, records, bullet and says ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 72 | 16 | 30 | 6653 | 734186 | 91996 | 1.02 | unknown | unknown | unknown | unknown |
| Each of the four suites resolves the shared file from the suite own location rather than the working directory, and each still prints its own count line ⟦added⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 14 | 26 | 7583 | 604959 | 89109 | 0.99 | unknown | unknown | unknown | unknown |
| No suite gains a dependency outside the repo, and the shared file keeps the plain-shell idiom: no test framework, each suite keeps its own pass/fail counters, FAIL - lines and count line ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 105 | 18 | 36 | 10168 | 932935 | 95867 | 1.16 | unknown | unknown | unknown | unknown |
| The Green comment records, for selection-order-recorded.test.sh and model-knobs-recorded.test.sh, which guarded passage was broken and the FAIL - line, failed count and non-zero exit observed ⟦added⟧ ⟦criterion 4⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 15 | 2 | 4 | 1100 | 58914 | 40504 | 0.36 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 2 | 0 | 41 | 0 | 1 | 1 | 1 | 0 | 2 | 2 | 4 | 1 | 1 | 1 | 1 | 1 | 0 | 2 | 44 | 0 | 44 | 0 | 2 | 1 | 1 | 1 | 44 | 1 | 1 | 2 | 2 | 2 | 0 | 0 | 1 | 1 |
| fast | 3 | 2 | 3 | 2 | 2 | 2 | 2 | 3 | 2 | 3 | 2 | 2 | 3 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 307 | 305 | 305 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 283 | 558 | 127932 | 13262267 | 1655164 | 18.45 |
