### 📊 Metrics — issue 275

Wall time for the issue: 10581 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/310.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 7 | 3 | 0 | 0 | 1493 | 383 | 52 | 98 | 24949 | 2373346 | 251532 | 3.96 |
| green | 6 | 3 | 0 | 0 | 5730 | 269 | 56 | 106 | 14537 | 2577187 | 202307 | 3.17 |
| refactor | 6 | 3 | 0 | 0 | 2392 | 192 | 45 | 90 | 15896 | 2119761 | 226081 | 2.44 |
| pin | 1 | 1 | 0 | 0 | 84 | 51 | 14 | 26 | 4431 | 700754 | 39806 | 0.35 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md's pin PASS branch runs the full suite (the run's <test-cmd>) after verify.sh pin PASSes and before tick-ledger.sh and the `git commit -m "test: pin` line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 306 | 47 | 92 | 16550 | 2266323 | 194414 | 3.00 | 3242 | unknown | 1/5 | nothing-structural |
| SKILL.md's pin PASS branch says a red full-suite run there bails as a system failure and never commits the pinned step ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 251 | 43 | 82 | 14862 | 1964104 | 193944 | 2.88 | 2298 | unknown | 0/5 | nothing-left |
| verify-pin.md's check 1 stays scoped to the target test alone, never a full-suite run ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 99 | 22 | 42 | 8596 | 1047059 | 81482 | 1.04 | unknown | unknown | unknown | unknown |
| a red full-suite run on the pin PASS branch has its own bail cause token, which classify-bail.sh classifies as system and SKILL.md's *Bailing* list names | 6 | 3 | 0 | 0 | 0 | 0 | 239 | 55 | 104 | 19805 | 2493562 | 249886 | 2.99 | 4221 | unknown | 1/5 | nothing-structural |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 167 | 320 | 59813 | 7771048 | 719726 | 9.91 |
