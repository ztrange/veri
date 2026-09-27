### 📊 Metrics — issue 500

Wall time for the issue: 1972 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/520.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 12 | 2 | 4 | 1234 | 56234 | 34492 | 0.31 |
| red | 10 | 5 | 0 | 0 | 389 | 303 | 81 | 160 | 29388 | 3770413 | 428696 | 4.77 |
| green | 10 | 5 | 0 | 0 | 531 | 354 | 103 | 204 | 33653 | 4662903 | 412880 | 4.91 |
| refactor | 10 | 5 | 0 | 0 | 310 | 215 | 60 | 120 | 20209 | 2571117 | 397596 | 4.10 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| Every developer prompt states the comment rule: a comment may only be a contract header (usage line and exit-code table) or a succinct warning where the shell itself is the hazard, and nothing else is written — no rationale, no issue archaeology, no restatement of the next line ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 188 | 50 | 100 | 17788 | 2399239 | 267048 | 2.97 | 318 | unknown | 0/5 | nothing-left |
| Every developer prompt states where rationale goes instead of a comment: a test first, an ADR second, and nowhere third ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 160 | 46 | 90 | 15458 | 2005319 | 247661 | 2.69 | 298 | unknown | 0/5 | nothing-left |
| The verify-green prompt tells the verifier to REJECT code carrying a rationale comment outside the two allowed classes ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 166 | 48 | 96 | 15320 | 2177240 | 242645 | 2.68 | 280 | unknown | 0/5 | nothing-left |
| The verify-refactor prompt tells the verifier to REJECT code carrying a rationale comment outside the two allowed classes ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 158 | 47 | 92 | 15100 | 2024168 | 238345 | 2.61 | 284 | unknown | 1/5 | structural-owed |
| The verify-green and verify-refactor prompts tell the verifier that a contract header or a shell-hazard warning is not grounds for REJECT ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 200 | 53 | 106 | 19584 | 2398467 | 243473 | 2.82 | 329 | unknown | 1/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 3 | 3 | 2 | 3 | 3 | 3 | 0 | 1 | 2 | 2 | 3 | 3 | 2 | 2 | 3 | 3 | 3 | 4 | 2 | 0 | 2 | 3 | 3 | 3 | 3 | 0 | 2 | 2 | 0 | 3 |
| fast | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 3 | 0 | 2 | 3 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 246 | 488 | 84484 | 11060667 | 1273664 | 14.09 |
