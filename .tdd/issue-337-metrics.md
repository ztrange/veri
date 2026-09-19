### 📊 Metrics — issue 337

Wall time for the issue: 1198 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/352.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 18 | 7 | 0 | 0 | 566 | 421 | 78 | 152 | 41897 | 2926719 | 687250 | 9.38 |
| green | 14 | 7 | 0 | 0 | 3580 | 255 | 75 | 144 | 22338 | 2770305 | 491485 | 6.86 |
| refactor | 16 | 7 | 0 | 0 | 1673 | 271 | 69 | 134 | 24500 | 2569466 | 569506 | 7.59 |
| pin | 4 | 4 | 0 | 0 | 105 | 58 | 15 | 30 | 5129 | 522843 | 136448 | 1.75 |

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
| affected-suites.sh <base>..<head> prints one suite path per line, sorted, with no duplicate, for a range git can resolve ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 122 | 27 | 54 | 11563 | 1020580 | 217342 | 2.97 | 1377 | unknown | 0/5 | nothing-left |
| A malformed argument (missing `..`, or either side not a resolvable revision) exits 2 with a diagnostic ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 112 | 29 | 54 | 10173 | 1005677 | 210159 | 2.86 | 792 | unknown | 0/5 | nothing-structural |
| A range whose diff is empty exits 3 and prints nothing ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 86 | 26 | 52 | 7132 | 958365 | 208846 | 2.75 | 717 | unknown | 0/5 | structural-owed |
| Rule 1: a change to skills/tdd/scripts/foo.sh with a suite skills/tdd/scripts/tests/foo.test.sh prints exactly that suite ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 10 | 20 | 4276 | 382394 | 70915 | 1.01 | unknown | unknown | unknown | unknown |
| Rule 1 via tests/unit/: a change to a script whose suite lives under skills/tdd/scripts/tests/unit/ prints that unit suite ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 8 | 16 | 3905 | 292989 | 71200 | 0.96 | unknown | unknown | unknown | unknown |
| Rule 2: a change to skills/tdd/scripts/lib/bar.sh prints the suite of every script that sources it, and no others ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 31 | 60 | 12649 | 1195929 | 221807 | 3.13 | 780 | unknown | 2/5 | structural-owed |
| Rule 3: a change to a suite file itself prints that suite ⟦criterion 6⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 40 | 9 | 18 | 3956 | 344502 | 72726 | 1.00 | unknown | unknown | unknown | unknown |
| Rule 3: a change to a fixture under tests/fixtures/ prints every suite that references the fixture by name ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 104 | 27 | 50 | 9892 | 939058 | 219373 | 2.91 | 743 | unknown | 1/5 | nothing-structural |
| Rule 4: a change to SKILL.md, CLAUDE.md, or Makefile prints their guard suites ⟦criterion 7⟧ | 8 | 3 | 0 | 0 | 1 | 0 | 155 | 34 | 68 | 14766 | 1355809 | 282915 | 3.88 | 8978 | unknown | 3/5 | nothing-left |
| Rule 5: a diff carrying one rule-1 file and one file no rule matches prints every suite (the full tier), not the rule-1 suite alone ⟦criterion 8⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 115 | 27 | 52 | 10169 | 975380 | 227515 | 3.02 | 794 | unknown | 0/5 | nothing-left |
| A diff touching only files rules 1–4 match never falls back to the full suite ⟦criterion 9⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 9 | 16 | 5383 | 318650 | 81891 | 1.11 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 237 | 460 | 93864 | 8789333 | 1884689 | 25.59 |
