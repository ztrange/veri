### 📊 Metrics — issue 2344

Wall time for the issue: 1589 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2391.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.87 over 45 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 93164 tokens, largest 127608 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.61 | 93164 |
| 2 | $0.03 | 94039 |
| 3 | $0.03 | 95988 |
| 4 | $0.02 | 96309 |
| 5 | $0.02 | 96665 |
| 6 | $0.02 | 97189 |
| 7 | $0.02 | 97703 |
| 8 | $0.02 | 98259 |
| 9 | $0.02 | 98677 |
| 10 | $0.05 | 102206 |
| 11 | $0.03 | 102938 |
| 12 | $0.02 | 103324 |
| 13 | $0.03 | 104097 |
| 14 | $0.03 | 104810 |
| 15 | $0.02 | 105303 |
| 16 | $0.03 | 106048 |
| 17 | $0.03 | 106963 |
| 18 | $0.03 | 107839 |
| 19 | $0.02 | 108209 |
| 20 | $0.03 | 109126 |
| 21 | $0.03 | 109784 |
| 22 | $0.03 | 110612 |
| 23 | $0.03 | 111876 |
| 24 | $0.02 | 112193 |
| 25 | $0.03 | 113063 |
| 26 | $0.03 | 113834 |
| 27 | $0.03 | 114736 |
| 28 | $0.03 | 115131 |
| 29 | $0.03 | 116163 |
| 30 | $0.03 | 116589 |
| 31 | $0.03 | 117388 |
| 32 | $0.03 | 118144 |
| 33 | $0.03 | 119035 |
| 34 | $0.03 | 120212 |
| 35 | $0.03 | 121201 |
| 36 | $0.03 | 122105 |
| 37 | $0.04 | 123553 |
| 38 | $0.03 | 123930 |
| 39 | $0.03 | 124905 |
| 40 | $0.03 | 125514 |
| 41 | $0.03 | 126004 |
| 42 | $0.03 | 126669 |
| 43 | $0.03 | 126950 |
| 44 | $0.03 | 127302 |
| 45 | $0.03 | 127608 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 8 | 5 | 1 | 2 | 611 | 0 | 30454 | 0.08 |
| red | 4 | 2 | 0 | 0 | 78 | 51 | 20 | 40 | 5108 | 579622 | 89525 | 0.33 |
| green | 4 | 2 | 0 | 0 | 219 | 37 | 16 | 32 | 4146 | 430755 | 57021 | 0.23 |
| refactor | 2 | 0 | 0 | 0 | 13 | 7 | 5 | 10 | 511 | 125962 | 27672 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 159 | 33 | 14 | 28 | 3591 | 332740 | 87335 | 0.29 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 159 | 67 | 28 | 56 | 6785 | 803599 | 117337 | 0.44 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `merge-lock.sh take` treats a lock as stale when its recorded pid is alive but the live process's start time differs from the one in the record, and reports it on stderr as `stale lock: <record>` exactly as it reports a dead holder today; pinned by a case whose faked holder pid is alive with a different recorded start time ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 51 | 20 | 40 | 5197 | 550743 | 98197 | 0.35 | 300 | unknown | 0/5 | nothing-left |  |  | full |
| `merge-lock.sh take` leaves no `.tdd/.merge.lock.*` staging directory behind on any exit, its exit 2 for a missing, unreadable or malformed holder record included; pinned by a broken-record case that checks no staging directory remains ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 44 | 21 | 42 | 4568 | 585596 | 76021 | 0.29 | 229 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `merge-lock.sh take` treats a lock as stale when its recorded pid is alive but the live process's start time differs from the one in the record, and reports it on stderr as `stale lock: <record>` exactly as it reports a dead holder today; pinned by a case whose faked holder pid is alive with a different recorded start time ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| `merge-lock.sh take` leaves no `.tdd/.merge.lock.*` staging directory behind on any exit, its exit 2 for a missing, unreadable or malformed holder record included; pinned by a broken-record case that checks no staging directory remains ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 6 | 4 | 3 | 3 | 4 | 4 |
| fast | 26 | 56 | 24 | 23 |  |  |  |  |
| target | 3 | 4 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 42 | 84 | 10376 | 1136339 | 204672 | 0.73 |
