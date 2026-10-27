### 📊 Metrics — issue 2457

Wall time for the issue: 508 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 4 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.72 over 37 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88659 tokens, largest 135103 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88659 |
| 2 | $0.03 | 90687 |
| 3 | $0.03 | 92587 |
| 4 | $0.02 | 92843 |
| 5 | $0.02 | 93122 |
| 6 | $0.02 | 93386 |
| 7 | $0.02 | 93644 |
| 8 | $0.02 | 94164 |
| 9 | $0.03 | 95362 |
| 10 | $0.03 | 96690 |
| 11 | $0.04 | 98735 |
| 12 | $0.03 | 100160 |
| 13 | $0.02 | 100472 |
| 14 | $0.03 | 101183 |
| 15 | $0.02 | 101657 |
| 16 | $0.02 | 101838 |
| 17 | $0.02 | 102410 |
| 18 | $0.03 | 103763 |
| 19 | $0.03 | 104602 |
| 20 | $0.03 | 105509 |
| 21 | $0.03 | 106729 |
| 22 | $0.03 | 108043 |
| 23 | $0.03 | 109207 |
| 24 | $0.03 | 109982 |
| 25 | $0.03 | 110631 |
| 26 | $0.02 | 110944 |
| 27 | $0.09 | 118811 |
| 28 | $0.04 | 120908 |
| 29 | $0.03 | 121470 |
| 30 | $0.03 | 122706 |
| 31 | $0.03 | 123477 |
| 32 | $0.03 | 124018 |
| 33 | $0.03 | 125217 |
| 34 | $0.05 | 127740 |
| 35 | $0.04 | 129404 |
| 36 | $0.04 | 131068 |
| 37 | $0.06 | 135103 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 910 | 0 | 33193 | 0.09 |
| red | 4 | 1 | 1 | 0 | 98 | 71 | 17 | 34 | 7616 | 546109 | 112729 | 0.56 |
| green | 3 | 0 | 1 | 0 | 149 | 65 | 15 | 28 | 5633 | 416327 | 73113 | 0.39 |
| red-missing | 1 | 0 | 0 | 0 | 31 | 21 | 4 | 8 | 2363 | 173314 | 36277 | 0.13 |
| pin | 1 | 0 | 1 | 0 | 18 | 12 | 3 | 6 | 1201 | 81291 | 16849 | 0.06 |
| exhausted | 1 | 0 | 0 | 0 | 23 | 16 | 3 | 6 | 1391 | 79591 | 14710 | 0.12 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 2 | 3 | 0 | 128 | 57 | 14 | 28 | 5526 | 358091 | 100050 | 0.34 |
| developer | claude-sonnet-5-5 | 2 | 0 | 0 | 0 | 55 | 38 | 8 | 16 | 4745 | 284498 | 81758 | 0.28 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 147 | 99 | 21 | 40 | 8843 | 654043 | 105063 | 0.73 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 98 | 0.56 |
| green | 0 | 0.00 | 149 | 0.39 |
| red-missing | 0 | 0.00 | 31 | 0.13 |
| pin | 0 | 0.00 | 18 | 0.06 |
| exhausted | 0 | 0.00 | 23 | 0.12 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| park-issue.sh given a PR URL whose owner or repo differs from the repository it runs in (its git origin) refuses with the usage line and exit 2, making no gh call of any kind; pinned by a process case running park-issue.sh against a gh stub that records every call, from a scratch git repo whose origin names another owner/repo ⟦criterion 1⟧ | 10 | 1 | 3 | 0 | 0 | 0 | 185 | 42 | 82 | 18204 | 1296632 | 253678 | 1.26 | unknown | green 1/2, red 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 4 | 8 | 4 | 1 | 5 |
| fast | 18 | 18 |  |  |  |  |  |
| target | 1 | 1 | 1 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 43 | 84 | 19114 | 1296632 | 286871 | 1.35 |
