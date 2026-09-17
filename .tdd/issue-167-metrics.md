### 📊 Metrics — issue 167

Wall time for the issue: 5104 s, from the first event of the log to the mark that ended the run.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/261.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 4 | 2 | 0 | 0 | 183 | 164 | 28 | 54 | 14479 | 1196063 | 146777 | 1.85 |
| green | 4 | 2 | 0 | 0 | 3777 | 187 | 26 | 48 | 7508 | 1049043 | 109216 | 1.88 |
| refactor | 4 | 2 | 0 | 0 | 980 | 171 | 32 | 64 | 11921 | 1626979 | 145453 | 1.46 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| For a green commit that changed `.tdd/issue-<n>.md` and two source files, a script that prints the commit's touched files for the refactor bounds names exactly the two source files, in `git diff` order, and never the ledger | 6 | 3 | 0 | 0 | 0 | 0 | 261 | 48 | 90 | 18870 | 2106225 | 215395 | 2.47 | 2000 | unknown | 0/5 | nothing-left |
| `SKILL.md` computes the refactor loop's touched-files list with that one script in both places — the cycle loop's first computation and Resume sub-step 2's recomputation from `$green` — so both give the same list and the `.tdd/` rule is stated once | 6 | 3 | 0 | 0 | 0 | 0 | 261 | 38 | 76 | 15038 | 1765860 | 186051 | 2.73 | 3086 | unknown | 0/5 | nothing-left |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 86 | 166 | 33908 | 3872085 | 401446 | 5.20 |
