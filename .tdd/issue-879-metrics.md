### 📊 Metrics — issue 879

Wall time for the issue: 1666 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/882.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 1 | 2 | 1148 | 11866 | 30068 | 0.13 |
| red | 8 | 3 | 0 | 0 | 514 | 358 | 74 | 144 | 32375 | 3679331 | 371497 | 3.84 |
| green | 6 | 3 | 0 | 0 | 467 | 190 | 49 | 98 | 16403 | 2243588 | 248424 | 2.23 |
| refactor | 6 | 3 | 0 | 0 | 253 | 114 | 32 | 62 | 8854 | 1300707 | 242237 | 1.89 |
| pin | 3 | 1 | 0 | 0 | 23 | 13 | 7 | 10 | 1338 | 161212 | 67317 | 0.31 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 11 | 0 | 0 | 398 | 174 | 55 | 104 | 17904 | 2022829 | 443130 | 2.36 |
| developer | claude-opus-5-5 | 11 | 0 | 0 | 0 | 871 | 511 | 108 | 212 | 42214 | 5373875 | 516413 | 6.05 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| gh_pr_ready <n> <head-sha> marks PR <n> ready only once GitHub's pulls/<n> reports <head-sha> as the PR's head: while it reports another sha it reads pulls/<n> again after VERI_POLL seconds and does not mark the PR ready meanwhile | 6 | 3 | 0 | 0 | 0 | 0 | 186 | 46 | 90 | 16350 | 2167265 | 259528 | 2.32 | 405 | unknown | 0/5 | nothing-left |  |  | full |
| gh_pr_ready <n> <head-sha> returns 2 without marking PR <n> ready when pulls/<n> still reports another sha after its bounded number of reads, with a stderr line naming both the expected and the reported sha | 6 | 3 | 0 | 0 | 0 | 0 | 207 | 45 | 90 | 17181 | 2101888 | 256709 | 2.30 | 426 | unknown | 1/5 | nothing-left |  |  | full |
| gh_pr_ready <n> called with no head-sha marks PR <n> ready at once, reading no pulls/<n>, exactly as before | 5 | 1 | 0 | 0 | 0 | 1 | 122 | 28 | 50 | 11043 | 1202473 | 165489 | 1.50 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's Draft PR step readies the PR with gh_pr_ready <pr-number> "$(git rev-parse HEAD)", so the ready_for_review CI run starts on the head just pushed rather than the pre-rebase sha | 6 | 3 | 0 | 0 | 0 | 0 | 160 | 43 | 84 | 14396 | 1913212 | 247749 | 2.15 | 400 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| gh_pr_ready <n> <head-sha> marks PR <n> ready only once GitHub's pulls/<n> reports <head-sha> as the PR's head: while it reports another sha it reads pulls/<n> again after VERI_POLL seconds and does not mark the PR ready meanwhile | 1 | 0/5 | nothing-left | PASS | 0 | 96 | 0.61 |
| gh_pr_ready <n> <head-sha> returns 2 without marking PR <n> ready when pulls/<n> still reports another sha after its bounded number of reads, with a stderr line naming both the expected and the reported sha | 1 | 1/5 | nothing-left | PASS | 0 | 109 | 0.70 |
| SKILL.md's Draft PR step readies the PR with gh_pr_ready <pr-number> "$(git rev-parse HEAD)", so the ready_for_review CI run starts on the head just pushed rather than the pre-rebase sha | 1 | 0/5 | nothing-left | PASS | 0 | 48 | 0.57 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 0 | 0 | 36 | 3 | 1 | 1 | 38 | 0 | 0 | 0 | 0 | 34 | 4 | 1 | 1 | 2 | 2 | 0 | 2 | 0 | 74 | 3 | 0 |
| fast | 15 | 15 | 14 | 14 | 15 | 14 | 14 | 15 | 15 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 163 | 316 | 60118 | 7396704 | 959543 | 8.41 |
