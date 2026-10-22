### 📊 Metrics — issue 2093

Wall time for the issue: 842 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2103.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 6 | 4 | 1 | 2 | 558 | 17051 | 12979 | 0.04 |
| red | 5 | 0 | 0 | 0 | 155 | 103 | 34 | 66 | 13823 | 1015244 | 97542 | 0.48 |
| pin | 5 | 5 | 0 | 0 | 83 | 40 | 15 | 30 | 4099 | 366301 | 61951 | 0.23 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 89 | 44 | 16 | 32 | 4657 | 383352 | 74930 | 0.27 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 155 | 103 | 34 | 66 | 13823 | 1015244 | 97542 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| ensure_run_state_ignored reached through a symlink in a scratch directory without the scripts still finds its scripts directory at the link's real target (the outcome its CLI or entry function gives, not one keyed to the link's directory), so realpath→abspath at its site turns the case red; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 42 | 12 | 24 | 5444 | 361366 | 33685 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| issue_worktree reached through a symlink in a scratch directory without the scripts still finds its scripts directory at the link's real target (the outcome its CLI or entry function gives, not one keyed to the link's directory), so realpath→abspath at its site turns the case red; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 8 | 16 | 2878 | 218854 | 31032 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| leaf_timeout reached through a symlink in a scratch directory without the scripts still finds its scripts directory at the link's real target (the outcome its CLI or entry function gives, not one keyed to the link's directory), so realpath→abspath at its site turns the case red; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 29 | 11 | 20 | 3657 | 289505 | 32058 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| preserve_attempt reached through a symlink in a scratch directory without the scripts still finds its scripts directory at the link's real target (the outcome its CLI or entry function gives, not one keyed to the link's directory), so realpath→abspath at its site turns the case red; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 10 | 20 | 3177 | 293148 | 32524 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| stop_run reached through a symlink in a scratch directory without the scripts still finds its scripts directory at the link's real target (the outcome its CLI or entry function gives, not one keyed to the link's directory), so realpath→abspath at its site turns the case red; no production change ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 22 | 8 | 16 | 2766 | 218672 | 30194 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 4 | 3 | 4 | 4 |  |  |  |  |  |
| target | 3 | 2 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 50 | 98 | 18480 | 1398596 | 172472 | 0.76 |
