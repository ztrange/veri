### 📊 Metrics — issue 223

Wall time for the issue: 5241 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/289.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 12 | 5 | 0 | 0 | 1224 | 838 | 116 | 218 | 64562 | 5763367 | 582380 | 8.45 |
| green | 9 | 4 | 0 | 1 | 10238 | 506 | 96 | 170 | 27135 | 4755393 | 353353 | 4.95 |
| refactor | 8 | 4 | 0 | 0 | 3488 | 456 | 74 | 140 | 27538 | 3569095 | 296208 | 4.40 |
| pin | 2 | 2 | 0 | 0 | 340 | 83 | 24 | 46 | 5356 | 1276832 | 78524 | 0.63 |

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
| build-verify-prompt.sh accepts an optional --step '<STEP>' flag before the positionals and every verify-*.md prompt it builds shows that step and says the verdict is about that criterion only ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 248 | 43 | 86 | 14986 | 2200592 | 203270 | 2.69 | 1686 | unknown | 1/5 | nothing-structural |
| verify.sh accepts --step '<STEP>' before its positionals and hands it to the verifier prompt, never reading ambient VERI_STEP into the prompt ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 282 | 55 | 100 | 20368 | 2548741 | 264383 | 3.13 | 2918 | unknown | 1/5 | nothing-structural |
| build-verify-prompt.sh takes the step only from --step: a VERI_STEP in the environment with no flag leaves no step in the prompt, and it has no parameter for the developer's rationale ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 112 | 22 | 42 | 8807 | 1064691 | 85630 | 1.23 | unknown | unknown | unknown | unknown |
| verify-refactor.md tells the verifier a shortfall against a criterion outside the step under judgement goes in REASON: as out of scope and is not by itself a REJECT ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 280 | 45 | 86 | 14084 | 2012292 | 200632 | 3.02 | 2146 | unknown | 0/5 | structural-owed |
| With no --step flag, build-verify-prompt.sh and verify.sh still build a valid verifier prompt for every phase with no unfilled step placeholder ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 179 | 28 | 50 | 12422 | 1514044 | 112031 | 1.64 | unknown | unknown | unknown | unknown |
| SKILL.md passes --step '<STEP>' on every verify.sh call the conductor makes (red, pin, green, refactor, revise re-verify, resume) | 9 | 4 | 0 | 1 | 1 | 0 | 782 | 117 | 210 | 53924 | 6024327 | 444519 | 6.71 | 11516 | unknown | 2/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 310 | 574 | 124591 | 15364687 | 1310465 | 18.42 |
