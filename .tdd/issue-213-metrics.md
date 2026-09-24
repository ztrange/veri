### 📊 Metrics — issue 213

Wall time for the issue: 1691 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/455.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 14 | 2 | 4 | 1108 | 54059 | 34895 | 0.31 |
| red | 6 | 2 | 0 | 0 | 269 | 234 | 48 | 92 | 23098 | 2229080 | 281977 | 3.16 |
| green | 4 | 2 | 0 | 0 | 494 | 146 | 39 | 76 | 14964 | 1724827 | 172509 | 2.02 |
| refactor | 4 | 2 | 0 | 0 | 283 | 101 | 25 | 48 | 9940 | 1015866 | 168916 | 1.75 |
| pin | 2 | 2 | 0 | 0 | 61 | 47 | 12 | 24 | 4848 | 500489 | 80105 | 0.84 |

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
| SKILL.md's launch section presents interactive and print mode as a trade the operator picks per run: interactive can be steered and costs ~25,000 tokens a request more, print mode is that much cheaper and turns every question into a bail ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 203 | 54 | 102 | 20124 | 2390975 | 267707 | 3.02 | 653 | unknown | 1/5 | structural-owed |
| No passage in SKILL.md says an interactive session is not where a run belongs while another says to pick interactive deliberately ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 168 | 42 | 82 | 16784 | 1785182 | 256357 | 2.74 | 435 | unknown | 0/5 | nothing-left |
| The reason SKILL.md gives for preferring print mode is the ~25,000-token per-request harness cost measured in #207, and no passage gives the CLAUDECODE nested-session refusal as that reason ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 86 | 14 | 28 | 8646 | 654744 | 92736 | 1.05 | unknown | unknown | unknown | unknown |
| SKILL.md still tells the operator, if a nested-launch guard fires, to run the conductor from a plain shell outside the session with claude -p "/tdd <n>", and skill-conductor-launch.test.sh stays green ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 71 | 14 | 28 | 7296 | 639361 | 86707 | 0.97 | unknown | unknown | unknown | unknown |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 76 | 2 | 77 | 0 | 76 | 0 | 77 | 0 | 1 | 0 | 77 | 0 | 77 | 0 | 0 | 1 | 0 |
| fast | 3 | 3 | 3 | 2 | 2 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 0 | 0 | 0 | 0 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 126 | 244 | 53958 | 5524321 | 738402 | 8.09 |
