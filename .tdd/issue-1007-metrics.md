### 📊 Metrics — issue 1007

Wall time for the issue: 984 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1239.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 9 | 2 | 4 | 1101 | 55710 | 36565 | 0.17 |
| cover | 1 | 0 | 0 | 0 | 16 | 11 | 4 | 8 | 1155 | 152885 | 37578 | 0.35 |
| transform | 2 | 1 | 0 | 0 | 92 | 29 | 13 | 24 | 3348 | 508594 | 80074 | 0.63 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 51 | 21 | 8 | 14 | 2590 | 259285 | 76485 | 0.38 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 70 | 28 | 11 | 22 | 3014 | 457904 | 77732 | 0.77 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Rename Function: `skills/tdd/scripts/veri/github.py`'s private `_gh_api(path)` becomes the public `gh_api(path)`, its three calls inside `github.py` following, and `skills/tdd/scripts/veri/wait_ci.py`'s two imports (the script form and the package form) and two calls following, with `_gh` still imported under its own name. Predicate: `! git grep -nw '_gh_api' skills/tdd/scripts/veri && grep -qE '^def gh_api\(path\):' skills/tdd/scripts/veri/github.py && grep -qE 'from \.github import .*\bgh_api\b' skills/tdd/scripts/veri/wait_ci.py && grep -qE 'from github import .*\bgh_api\b' skills/tdd/scripts/veri/wait_ci.py && grep -qE 'from \.github import .*\b_gh\b' skills/tdd/scripts/veri/wait_ci.py` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 40 | 17 | 32 | 4503 | 661479 | 117652 | 0.99 | 142 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 1 | 33 | 22 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 19 | 36 | 5604 | 717189 | 154217 | 1.16 |
