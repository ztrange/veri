### 📊 Metrics — issue 1553

Wall time for the issue: 2179 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1555.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 11 | 1 | 2 | 868 | 12193 | 42345 | 0.18 |
| red | 4 | 1 | 0 | 0 | 126 | 102 | 27 | 54 | 10321 | 1424916 | 201780 | 1.05 |
| green | 4 | 1 | 1 | 0 | 390 | 113 | 27 | 54 | 11820 | 1530377 | 173574 | 1.36 |
| refactor | 2 | 1 | 0 | 0 | 142 | 60 | 17 | 34 | 4428 | 878399 | 91922 | 0.50 |
| pin | 2 | 2 | 0 | 0 | 33 | 23 | 7 | 14 | 2387 | 291509 | 87747 | 0.40 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 6 | 1 | 0 | 403 | 114 | 30 | 60 | 10555 | 1412362 | 276216 | 1.35 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 155 | 125 | 34 | 68 | 11623 | 1838212 | 204645 | 1.12 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 149 | 70 | 15 | 30 | 7646 | 886820 | 116507 | 1.03 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 390 | 1.36 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A failed read of a PR's checks (the PR, its check-runs or its status, answered non-zero by gh) counts as one pending poll: wait-ci.sh sleeps its poll interval and reads again within the same slice and deadline, so a faked gh that fails twice and then answers green gets exit 0 ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 215 | 56 | 112 | 20014 | 3037716 | 365448 | 2.36 | 707 | 1/2 | 1/5 | nothing-structural |  |  | full |
| wait-ci.sh exits 2 ("could not read the checks of …") only after three consecutive polls whose read failed: a faked gh that always fails gets exit 2 after exactly three reads ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 13 | 26 | 4492 | 665751 | 94725 | 0.49 | unknown | unknown | unknown | unknown |  |  | pin |
| A successful poll resets the consecutive-failure count, so failures that don't come three in a row never end the wait: a faked gh that alternates failure and pending, then answers green, gets exit 0 ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 9 | 18 | 4450 | 421734 | 94850 | 0.47 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A failed read of a PR's checks (the PR, its check-runs or its status, answered non-zero by gh) counts as one pending poll: wait-ci.sh sleeps its poll interval and reads again within the same slice and deadline, so a faked gh that fails twice and then answers green gets exit 0 ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 142 | 0.50 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 9 | 1 | 1 | 9 | 1 |  |
| target | 1 | 1 | 0 | 0 | 1 | 0 | 1 |
| fast | 57 | 55 | 57 | 57 |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 79 | 158 | 29824 | 4137394 | 597368 | 3.50 |
