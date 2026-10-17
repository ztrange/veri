### 📊 Metrics — issue 1463

Wall time for the issue: 1342 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 1 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1682.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 15 | 4 | 8 | 1740 | 182212 | 47772 | 0.23 |
| red | 1 | 0 | 0 | 0 | 47 | 35 | 8 | 16 | 4263 | 500413 | 64495 | 0.35 |
| pin | 1 | 1 | 0 | 0 | 51 | 32 | 8 | 14 | 3223 | 362423 | 50169 | 0.27 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 71 | 47 | 12 | 22 | 4963 | 544635 | 97941 | 0.50 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 47 | 35 | 8 | 16 | 4263 | 500413 | 64495 | 0.35 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A medium pytest case marked `@pytest.mark.process(...)` runs SKILL.md's verdict launch end to end through the real detach-leaf.sh, supervise.sh, run-verdict.sh, verify.sh and wait-leaf.sh, with only `claude` stubbed through CLAUDE_BIN and no production change: a stub verifier answering `VERDICT: PASS` makes `wait-leaf.sh verdict-<phase>` exit 0 and one answering `VERDICT: REJECT` makes it exit 1, and in both the verifier's reason is in `.tdd/verify-<phase>.reason`; the case goes red when the hand-off between any two of those scripts is broken ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 67 | 16 | 30 | 7486 | 862836 | 114664 | 0.62 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| target | 2 | 2 | 2 | 1 | 3 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 20 | 38 | 9226 | 1045048 | 162436 | 0.85 |
