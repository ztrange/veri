### 📊 Metrics — issue 484

Wall time for the issue: 964 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/509.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 12 | 2 | 4 | 1092 | 56283 | 35092 | 0.31 |
| red | 5 | 1 | 0 | 0 | 172 | 142 | 41 | 82 | 13673 | 1889374 | 206853 | 2.31 |
| green | 2 | 1 | 0 | 0 | 77 | 58 | 16 | 30 | 5979 | 663988 | 82369 | 0.91 |
| refactor | 2 | 1 | 0 | 0 | 44 | 27 | 8 | 16 | 2622 | 306450 | 76225 | 0.72 |
| pin | 3 | 3 | 0 | 0 | 64 | 48 | 11 | 20 | 4863 | 354426 | 111309 | 1.06 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| next-unchecked.sh prints an unchecked ledger line whose text quotes the full-suite or the human-owed marker mid-sentence, rather than skipping it ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 131 | 37 | 72 | 12846 | 1555705 | 239578 | 2.48 | 269 | unknown | 0/5 | nothing-left |
| next-unchecked.sh still skips an unchecked ledger line carrying the full-suite or the human-owed marker in the written position, immediately before its criterion mark ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 12 | 24 | 4233 | 519991 | 77953 | 0.81 | unknown | unknown | unknown | unknown |
| next-unchecked.sh skips a line that carries a marker in the written position and also quotes one elsewhere in its text ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 14 | 26 | 5233 | 575737 | 80208 | 0.86 | unknown | unknown | unknown | unknown |
| next-unchecked.sh still prints the first unchecked line and exits 3 with no output when no unchecked line remains ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 13 | 26 | 4825 | 562805 | 79017 | 0.84 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| fast | 3 | 3 | 3 | 3 |  |  |  |  |
| target | 0 | 1 | 0 | 0 | 1 | 0 | 1 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 78 | 152 | 28229 | 3270521 | 511848 | 5.31 |
