### 📊 Metrics — issue 2477

Wall time for the issue: 1688 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2484.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.83 over 39 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88646 tokens, largest 135844 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88646 |
| 2 | $0.03 | 90468 |
| 3 | $0.03 | 92472 |
| 4 | $0.02 | 92875 |
| 5 | $0.02 | 93238 |
| 6 | $0.02 | 93654 |
| 7 | $0.02 | 93980 |
| 8 | $0.02 | 94565 |
| 9 | $0.02 | 94934 |
| 10 | $0.04 | 97089 |
| 11 | $0.06 | 102777 |
| 12 | $0.03 | 103487 |
| 13 | $0.03 | 104554 |
| 14 | $0.03 | 106097 |
| 15 | $0.02 | 106524 |
| 16 | $0.03 | 107094 |
| 17 | $0.03 | 107662 |
| 18 | $0.03 | 108270 |
| 19 | $0.03 | 109088 |
| 20 | $0.11 | 120209 |
| 21 | $0.03 | 121030 |
| 22 | $0.03 | 121734 |
| 23 | $0.03 | 122558 |
| 24 | $0.04 | 123989 |
| 25 | $0.04 | 126424 |
| 26 | $0.03 | 127257 |
| 27 | $0.03 | 127665 |
| 28 | $0.03 | 128273 |
| 29 | $0.03 | 128872 |
| 30 | $0.03 | 129791 |
| 31 | $0.03 | 130480 |
| 32 | $0.03 | 131350 |
| 33 | $0.04 | 132559 |
| 34 | $0.03 | 133350 |
| 35 | $0.03 | 134098 |
| 36 | $0.03 | 134617 |
| 37 | $0.03 | 134892 |
| 38 | $0.03 | 135453 |
| 39 | $0.03 | 135844 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 8 | 1 | 2 | 963 | 0 | 32854 | 0.09 |
| diff | 4 | 2 | 0 | 0 | 441 | 105 | 33 | 66 | 8333 | 1063729 | 107740 | 0.46 |
| red | 2 | 0 | 0 | 0 | 91 | 58 | 15 | 30 | 5352 | 501285 | 42978 | 0.21 |
| pin | 2 | 2 | 0 | 0 | 58 | 36 | 9 | 18 | 2694 | 254272 | 31101 | 0.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 148 | 68 | 18 | 36 | 5819 | 462260 | 112920 | 0.39 |
| developer | claude-sonnet-5-5 | 4 | 0 | 0 | 0 | 455 | 139 | 40 | 80 | 11523 | 1357026 | 101753 | 0.51 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The verify-green prompt template gains a clause: a judgement that a change is or is not covered by a case is made by running the fast command it was given ({{FAST_CMD}}) and the affected suites, never one test file alone, and a REJECT on that ground names the exact command that was run ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 80 | 24 | 48 | 6356 | 807861 | 77293 | 0.34 | 400 | n/a | n/a | n/a |  |  | full |
| A build-verify-prompt case asserts the rendered verify-green prompt carries the coverage-probe clause (fast command plus affected suites, never one test file, a REJECT names the command run) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 11 | 22 | 3759 | 340680 | 36546 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| The verify-refactor and verify-diff prompt templates gain the same coverage-probe clause the verify-green prompt carries, on their fast command and affected suites ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 9 | 18 | 1977 | 255868 | 30447 | 0.12 | 134 | n/a | n/a | n/a |  |  | full |
| Build-verify-prompt cases assert the rendered verify-refactor and verify-diff prompts each carry the coverage-probe clause ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 13 | 26 | 4287 | 414877 | 37533 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast | 22 | 18 | 18 | 26 |  |
| affected | 4 | 5 | 6 | 8 |  |
| target | 4 | 3 | 1 | 1 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 58 | 116 | 17342 | 1819286 | 214673 | 0.89 |
