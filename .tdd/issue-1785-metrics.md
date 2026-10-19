### 📊 Metrics — issue 1785

Wall time for the issue: 2014 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1811.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 20 | 4 | 8 | 2328 | 116733 | 16442 | 0.08 |
| diff | 4 | 2 | 0 | 0 | 573 | 92 | 29 | 56 | 10034 | 935809 | 86681 | 0.41 |
| red | 5 | 2 | 0 | 0 | 131 | 93 | 28 | 56 | 10758 | 895829 | 101414 | 0.45 |
| pin | 2 | 2 | 0 | 0 | 39 | 32 | 9 | 18 | 2976 | 256700 | 31844 | 0.14 |
| green | 5 | 1 | 1 | 0 | 217 | 115 | 38 | 74 | 10903 | 1217979 | 100124 | 0.60 |
| red-contradicted | 1 | 0 | 0 | 0 | 35 | 25 | 5 | 10 | 3261 | 161672 | 22333 | 0.10 |
| refactor | 2 | 1 | 0 | 0 | 30 | 12 | 5 | 10 | 987 | 129411 | 29083 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 1 | 0 | 384 | 160 | 49 | 98 | 15156 | 1452344 | 170379 | 0.72 |
| developer | claude-sonnet-5-5 | 10 | 0 | 0 | 0 | 664 | 229 | 69 | 134 | 26091 | 2261789 | 217542 | 1.15 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 217 | 0.60 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The `## Launching the conductor` section (skills/tdd/SKILL.md:201-262) moves verbatim into README.md as a `## Launching the conductor` section placed right after `## Install`, reworded only where its new place requires (a path the operator types from the repository, not `$S`), and SKILL.md no longer carries that heading or its `**Three launch modes`, `**The skill snapshot:` and `**The record survives only a run` paragraphs; in the same commit `tests/py/unit/test_skill_conductor_launch.py` and `tests/py/unit/test_skill_commit.py` (test_865, test_866 and its LAUNCH heading) read that text from the repository's README.md instead of SKILL.md, keeping all seven cases' outcome green and none of them passing by finding nothing to check; no production script changes ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 18 | 34 | 6402 | 606913 | 50748 | 0.25 | 376 | n/a | n/a | n/a |  |  | full |
| A small pytest case pins that skills/tdd/SKILL.md carries no `## Launching the conductor` heading and none of the lines `**Three launch modes`, `**The skill snapshot:`, `**The record survives only a run`, while README.md carries a `## Launching the conductor` section after `## Install` holding all three ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 9 | 18 | 3064 | 266067 | 33579 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md's *The scripts* paragraph on the pinned `$S` names README.md's *Launching the conductor* in place of "see *The skill snapshot* below", and preflight step 2's `leaf-launchable.sh` exit-2 branch names README.md's *Launching the conductor* in place of "the case *Launching the conductor* above describes" and still says veri never unsets `CLAUDECODE` or any other such guard itself; pinned by a small pytest case ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 13 | 26 | 5646 | 416588 | 38330 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| `affected-suites.sh` places an edit to `README.md` on the suites that read it (test_skill_conductor_launch.py and test_skill_commit.py among them) instead of raising Unplaced and widening to every suite; pinned by a case in the affected-suites tests ⟦criterion 3⟧ | 11 | 4 | 1 | 0 | 0 | 0 | 199 | 63 | 124 | 20175 | 1978936 | 212889 | 1.05 | 552 | 2/2 | 0/5 | nothing-left |  |  | full |
| `unreachable.sh` prints the same lines at the branch point and at HEAD, and test_skill_conductor_launch.py and test_skill_commit.py read README.md with every one of their cases asserting on text it actually finds; no commit is needed when that already holds ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 11 | 22 | 3632 | 328896 | 35933 | 0.16 | 268 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `affected-suites.sh` places an edit to `README.md` on the suites that read it (test_skill_conductor_launch.py and test_skill_commit.py among them) instead of raising Unplaced and widening to every suite; pinned by a case in the affected-suites tests ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 30 | 0.10 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 9 | 6 | 7 | 8 | 8 | 8 | 11 |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 146 | 0 | 113 | 1 | 1 | 0 | 7 | 0 | 5 | 1 | 5 | 7 | 7 | 0 | 5 | 0 | 5 | 6 | 159 |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 7 |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 118 | 232 | 41247 | 3714133 | 387921 | 1.87 |
