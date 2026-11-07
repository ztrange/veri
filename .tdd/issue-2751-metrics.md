### 📊 Metrics — issue 2751

Wall time for the issue: 3344 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3203.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.32 over 52 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 92840 tokens, largest 146819 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.61 | 92840 |
| 2 | $0.08 | 100305 |
| 3 | $0.03 | 101583 |
| 4 | $0.04 | 103488 |
| 5 | $0.04 | 105912 |
| 6 | $0.02 | 106312 |
| 7 | $0.02 | 106660 |
| 8 | $0.02 | 106872 |
| 9 | $0.02 | 107127 |
| 10 | $0.02 | 107349 |
| 11 | $0.02 | 107602 |
| 12 | $0.03 | 108223 |
| 13 | $0.05 | 111811 |
| 14 | $0.03 | 112217 |
| 15 | $0.03 | 112831 |
| 16 | $0.03 | 113543 |
| 17 | $0.03 | 114776 |
| 18 | $0.03 | 115884 |
| 19 | $0.03 | 116294 |
| 20 | $0.03 | 116860 |
| 21 | $0.03 | 117241 |
| 22 | $0.03 | 117527 |
| 23 | $0.03 | 118810 |
| 24 | $0.03 | 119665 |
| 25 | $0.03 | 120558 |
| 26 | $0.03 | 120770 |
| 27 | $0.04 | 122141 |
| 28 | $0.04 | 123514 |
| 29 | $0.03 | 123885 |
| 30 | $0.03 | 124077 |
| 31 | $0.04 | 126140 |
| 32 | $0.03 | 126844 |
| 33 | $0.03 | 127666 |
| 34 | $0.03 | 128266 |
| 35 | $0.04 | 129923 |
| 36 | $0.03 | 130755 |
| 37 | $0.03 | 131509 |
| 38 | $0.10 | 140922 |
| 39 | $0.03 | 141382 |
| 40 | $0.03 | 141734 |
| 41 | $0.04 | 142606 |
| 42 | $0.03 | 143392 |
| 43 | $0.03 | 143827 |
| 44 | $0.03 | 144078 |
| 45 | $0.03 | 144332 |
| 46 | $0.03 | 144658 |
| 47 | $0.03 | 145319 |
| 48 | $0.03 | 145567 |
| 49 | $0.03 | 145823 |
| 50 | $0.03 | 146083 |
| 51 | $0.03 | 146435 |
| 52 | $0.03 | 146819 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 11 | 2 | 4 | 1374 | 18401 | 19042 | 0.06 |
| prose | 5 | 0 | 0 | 0 | 38 | 25 | 5 | 10 | 3264 | 16483 | 39406 | 0.13 |
| skill-edit | 1 | 0 | 0 | 0 | 18 | 15 | 5 | 8 | 1394 | 52725 | 19928 | 0.07 |
| red | 1 | 0 | 0 | 0 | 33 | 19 | 5 | 10 | 2200 | 80645 | 15137 | 0.07 |
| pin | 1 | 0 | 1 | 0 | 48 | 22 | 6 | 10 | 2117 | 74898 | 13981 | 0.06 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 1 | 1 | 0 | 62 | 33 | 8 | 14 | 3491 | 93299 | 33023 | 0.13 |
| developer | claude-sonnet-5-5 | 1 | 0 | 0 | 0 | 33 | 19 | 5 | 10 | 2200 | 80645 | 15137 | 0.07 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 33 | 0.07 |
| pin | 0 | 0.00 | 48 | 0.06 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| skills/vstatus/SKILL.md runs `status.sh --report` once and prints its output verbatim, naming no other read and spawning no subagent; issue data comes from the snapshot the report reads (its age in the Queue section) and the skill never runs `report-cache.sh refresh`; a live run is defined by pointing at the report's Running section; on `status.sh --report` exit 2 it reports that and stops with no figures of its own — REQUIREMENTS.md rows A4, A5, A6 rewritten and A11 added, rows A7, A8, A9 and A10 deleted, A1 to A3 kept, and the unit regraded ⟦skill-edit⟧ ⟦criterion 1⟧ | 5 | 0 | 0 | 0 | 0 | 0 | 35 | 9 | 16 | 3988 | 67692 | 49930 | 0.17 | 117 | unknown | unknown | unknown |  |  | full |
| README.md and CLAUDE.md name none of the reads /vstatus no longer makes (`report-cache.sh refresh`, `status.sh --json`, `metrics.sh` per running issue, a `git tag` or `gh pr list` read for the status report, a status subagent) as reads of /vstatus, pinned by a small unit-tier case in a new skills/tdd/scripts/tests/py/unit/test_vstatus_docs_reads.py ⟦criterion 2⟧ | 2 | 0 | 1 | 0 | 0 | 0 | 41 | 11 | 20 | 4317 | 155543 | 29118 | 0.13 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 5 |  |  |
| target | 5 | 5 | 5 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 23 | 42 | 10349 | 243152 | 107494 | 2.72 (estimate) |
