### 📊 Metrics — issue 108

Wall time for the issue: 1309 s, from the first event of the log to the mark that ended the run.
Steps done: 10 of 10 planned.
Outcome: the run bailed — poisoned-baseline, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 22 | 11 | 0 | 0 | 2622 | 2581 | 243 | 464 | 187491 | 11642061 | 1020563 | 17.58 |
| green | 23 | 8 | 1 | 0 | 10146 | 2097 | 295 | 578 | 128200 | 14938766 | 903831 | 17.70 |
| refactor | 20 | 10 | 0 | 0 | 4899 | 2327 | 335 | 640 | 168907 | 18704883 | 1046337 | 19.37 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 31 | 0.19 |
| green | 3041 | 3.46 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| metrics.sh renders a markdown table of per-phase attempts, verdicts PASS/REJECT and kills from the event log | 9 | 3 | 0 | 0 | 0 | 809 | 95 | 160 | 55971 | 3833098 | 340471 | 6.20 | 6404 | unknown | unknown | unknown |
| the table carries a per-step section with the same counts, plus stuck retries used | 6 | 3 | 0 | 0 | 0 | 676 | 88 | 174 | 50729 | 4568714 | 252879 | 5.26 | 1483 | unknown | unknown | unknown |
| the table reports revise attempts used of REVISE_BUDGET and refactor transforms used of VERI_REFACTOR_BUDGET, and whether the refactor loop stopped by budget | 6 | 3 | 0 | 0 | 0 | 794 | 87 | 174 | 57430 | 4826675 | 306092 | 5.63 | 1472 | unknown | unknown | unknown |
| the table reports wall seconds and API seconds per phase and per step, and the issue's wall time from its first event to done or bail | 5 | 2 | 0 | 0 | 0 | 806 | 94 | 184 | 58023 | 5597981 | 284567 | 6.36 | 1490 | unknown | unknown | unknown |
| the table reports wall seconds and API seconds per phase and per step, and the issue wall time from its first event to done or bail | 1 | 1 | 0 | 0 | 0 | 30 | 6 | 12 | 1915 | 266361 | 29812 | 0.19 | unknown | unknown | unknown | unknown |
| the table reports turns, the four token counts and dollars per phase, per step and in total, with a line saying whether the conductor's own cost is included | 6 | 3 | 0 | 0 | 0 | 916 | 97 | 190 | 68184 | 6027004 | 369883 | 6.85 | 1806 | unknown | unknown | unknown |
| a step recovered after a REJECT contributes its rejected attempts to rework per phase and nothing to waste | 8 | 2 | 1 | 0 | 0 | 1042 | 97 | 182 | 58278 | 5109208 | 357961 | 7.30 | 3831 | 1/2 | unknown | unknown |
| a bailed step contributes every attempt, PASS verdicts included, to waste per phase and nothing to rework | 6 | 3 | 0 | 0 | 0 | 378 | 73 | 138 | 26366 | 3352670 | 261872 | 3.68 | 1041 | unknown | unknown | unknown |
| the table reports steps done of planned and the issue's outcome, a bail split system or process | 6 | 3 | 0 | 0 | 0 | 756 | 103 | 206 | 53631 | 5819244 | 309402 | 6.18 | 1461 | unknown | unknown | unknown |
| a figure a missing conductor mark makes unreadable renders as unknown, never as zero | 6 | 3 | 0 | 0 | 0 | 363 | 73 | 146 | 23629 | 3282647 | 229244 | 3.49 | 1163 | unknown | unknown | unknown |
| SKILL.md has the conductor commit issue-<n>-metrics.md in one metrics: commit before the PR and append the 📊 Metrics block to the final comment and PR body, and on a bail commit it on the pushed branch with the block on the bail comment | 6 | 3 | 0 | 0 | 0 | 435 | 60 | 116 | 30442 | 2602108 | 228548 | 3.53 | 1827 | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 873 | 1682 | 484598 | 45285710 | 2970731 | 54.66 |
