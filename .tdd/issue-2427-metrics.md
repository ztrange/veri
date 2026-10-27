### 📊 Metrics — issue 2427

Wall time for the issue: 3599 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2512.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.01 over 80 turns, in 2 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88681 tokens, largest 101057 tokens
Conductor context: first turn 88658 tokens, largest 171485 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 88681 |
| 2 | $0.04 | 90878 |
| 3 | $0.04 | 92797 |
| 4 | $0.03 | 93130 |
| 5 | $0.03 | 93545 |
| 6 | $0.03 | 93838 |
| 7 | $0.03 | 94182 |
| 8 | $0.04 | 95954 |
| 9 | $0.04 | 97775 |
| 10 | $0.03 | 98299 |
| 11 | $0.05 | 101057 |
| 12 | $0.57 | 88658 |
| 13 | $0.04 | 91074 |
| 14 | $0.03 | 92705 |
| 15 | $0.03 | 93674 |
| 16 | $0.02 | 94257 |
| 17 | $0.02 | 94696 |
| 18 | $0.02 | 95201 |
| 19 | $0.02 | 95894 |
| 20 | $0.02 | 96258 |
| 21 | $0.02 | 96553 |
| 22 | $0.02 | 97133 |
| 23 | $0.02 | 97672 |
| 24 | $0.04 | 99609 |
| 25 | $0.13 | 113045 |
| 26 | $0.03 | 114544 |
| 27 | $0.05 | 117412 |
| 28 | $0.03 | 118505 |
| 29 | $0.03 | 118867 |
| 30 | $0.03 | 119664 |
| 31 | $0.03 | 120181 |
| 32 | $0.03 | 120628 |
| 33 | $0.03 | 121253 |
| 34 | $0.04 | 122607 |
| 35 | $0.03 | 122836 |
| 36 | $0.03 | 123695 |
| 37 | $0.03 | 124083 |
| 38 | $0.03 | 124763 |
| 39 | $0.03 | 125714 |
| 40 | $0.03 | 126394 |
| 41 | $0.03 | 127471 |
| 42 | $0.03 | 128112 |
| 43 | $0.03 | 128785 |
| 44 | $0.03 | 129123 |
| 45 | $0.03 | 130028 |
| 46 | $0.03 | 130481 |
| 47 | $0.03 | 131126 |
| 48 | $0.04 | 132958 |
| 49 | $0.09 | 141148 |
| 50 | $0.04 | 142527 |
| 51 | $0.04 | 144062 |
| 52 | $0.04 | 144924 |
| 53 | $0.04 | 146018 |
| 54 | $0.04 | 147704 |
| 55 | $0.04 | 148594 |
| 56 | $0.04 | 149452 |
| 57 | $0.04 | 150448 |
| 58 | $0.04 | 151630 |
| 59 | $0.04 | 152382 |
| 60 | $0.04 | 153545 |
| 61 | $0.03 | 153952 |
| 62 | $0.04 | 155143 |
| 63 | $0.05 | 157004 |
| 64 | $0.04 | 157885 |
| 65 | $0.05 | 159669 |
| 66 | $0.04 | 160483 |
| 67 | $0.04 | 161792 |
| 68 | $0.04 | 162512 |
| 69 | $0.04 | 163340 |
| 70 | $0.04 | 164699 |
| 71 | $0.06 | 167780 |
| 72 | $0.04 | 168481 |
| 73 | $0.04 | 168786 |
| 74 | $0.04 | 169433 |
| 75 | $0.04 | 169823 |
| 76 | $0.04 | 170113 |
| 77 | $0.04 | 170360 |
| 78 | $0.04 | 170812 |
| 79 | $0.04 | 171167 |
| 80 | $0.04 | 171485 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 11 | 1 | 2 | 1348 | 0 | 33919 | 0.10 |
| red | 10 | 3 | 1 | 0 | 338 | 234 | 55 | 106 | 23411 | 1724547 | 242076 | 1.30 |
| green | 6 | 3 | 0 | 0 | 372 | 122 | 31 | 60 | 8633 | 925759 | 108658 | 0.45 |
| refactor | 4 | 1 | 0 | 0 | 76 | 36 | 12 | 24 | 2040 | 338280 | 67125 | 0.22 |
| pin | 1 | 1 | 0 | 0 | 22 | 11 | 4 | 8 | 1194 | 114345 | 16655 | 0.07 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 9 | 1 | 0 | 366 | 152 | 36 | 70 | 12442 | 994189 | 176575 | 0.67 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 304 | 151 | 47 | 92 | 12540 | 1465299 | 195023 | 0.76 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 152 | 111 | 20 | 38 | 11644 | 643443 | 96835 | 0.71 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 152 | 0.56 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| classify-bail.sh labels the external-kill cause `killed-external` as `system`, distinct from the process causes and printed on its own line like every other cause ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 95 | 20 | 38 | 4616 | 539055 | 105034 | 0.36 | 299 | unknown | 0/5 | nothing-left |  |  | full |
| When a supervised leaf is SIGKILLed by a process other than veri (veri issued no kill), supervise.sh notices it without waiting out the heartbeat or hard timeout, exits 2, does not retry it under VERI_STUCK_RETRIES, and its `exit` event carries `cause=killed-external` rather than a stuck cause — pinned by a medium case (a real stub leaf killed externally, `@pytest.mark.process`) that reads the cause from the event log ⟦criterion 1⟧ | 8 | 2 | 1 | 0 | 0 | 0 | 181 | 41 | 80 | 18525 | 1294113 | 176795 | 1.05 | 546 | 2/2 | 0/5 | nothing-left |  |  | full |
| stop-reason.sh, for an ended run whose latest leaf `exit` event in the run's event log carries `cause=killed-external`, prints `killed-external <leaf name>` as the run's cause line in place of the cause line it would otherwise print, so the report names an external kill rather than stuckness; a run whose latest leaf exit carries no such cause is reported as before ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 89 | 30 | 58 | 8006 | 913153 | 111704 | 0.45 | 317 | unknown | 1/5 | nothing-left |  |  | full |
| When veri's own stuck-kill issues the SIGKILL (heartbeat silence or hard timeout), the supervisor still records the leaf as killed-stuck with the stuck reason as its `exit` cause, still exits 2, and VERI_STUCK_RETRIES still bounds its retries — no SIGKILL is reclassified as external merely for being a SIGKILL ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 11 | 22 | 4131 | 356610 | 40981 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| classify-bail.sh labels the external-kill cause `killed-external` as `system`, distinct from the process causes and printed on its own line like every other cause ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |
| When a supervised leaf is SIGKILLed by a process other than veri (veri issued no kill), supervise.sh notices it without waiting out the heartbeat or hard timeout, exits 2, does not retry it under VERI_STUCK_RETRIES, and its `exit` event carries `cause=killed-external` rather than a stuck cause — pinned by a medium case (a real stub leaf killed externally, `@pytest.mark.process`) that reads the cause from the event log ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.06 |
| stop-reason.sh, for an ended run whose latest leaf `exit` event in the run's event log carries `cause=killed-external`, prints `killed-external <leaf name>` as the run's cause line in place of the cause line it would otherwise print, so the report names an external kill rather than stuckness; a run whose latest leaf exit carries no such cause is reported as before ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 60 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 2 | 2 | 3 | 4 | 7 | 7 | 4 | 7 | 12 | 13 | 15 | 16 | 3 | 3 | 2 | 4 | 3 | 2 | 5 |
| fast | 24 | 25 | 26 | 26 | 24 | 25 | 24 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 7 | 2 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 103 | 200 | 36626 | 3102931 | 468433 | 2.14 |
