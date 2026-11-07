### 📊 Metrics — issue 3059

Wall time for the issue: 5769 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3195.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 16 | 5 | 10 | 1643 | 129561 | 34938 | 0.12 |
| red | 11 | 5 | 0 | 0 | 385 | 246 | 61 | 116 | 22829 | 1746974 | 212697 | 0.93 |
| green | 11 | 4 | 1 | 0 | 685 | 208 | 69 | 134 | 16965 | 1957765 | 174602 | 0.80 |
| red-missing | 1 | 0 | 0 | 0 | 16 | 13 | 3 | 6 | 1893 | 79718 | 15313 | 0.07 |
| pin | 3 | 3 | 0 | 0 | 66 | 47 | 11 | 22 | 4606 | 290109 | 42932 | 0.18 |
| refactor | 5 | 1 | 0 | 0 | 75 | 38 | 16 | 32 | 3318 | 425799 | 73910 | 0.26 |
| diff | 2 | 1 | 0 | 0 | 164 | 68 | 22 | 44 | 6745 | 795377 | 42217 | 0.25 |
| red-contradicted | 1 | 0 | 0 | 0 | 38 | 32 | 6 | 12 | 3668 | 188102 | 19992 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 16 | 15 | 1 | 0 | 706 | 272 | 69 | 134 | 21885 | 1818606 | 257797 | 1.05 |
| developer | claude-sonnet-5-5 | 19 | 0 | 0 | 0 | 741 | 396 | 124 | 242 | 39782 | 3794799 | 358804 | 1.67 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 295 | 0.30 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The first line of `status.sh --report` names the machine's local zone once, with its UTC offset, e.g. `CST (UTC−6)` under `TZ=America/Chicago` on a winter date (a small case, in-process, no git) ⟦criterion 1⟧ | 9 | 3 | 1 | 0 | 0 | 0 | 137 | 43 | 82 | 12890 | 1139346 | 155582 | 0.63 | 562 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| When `.tdd/status-last` exists, the report's first line opens with the window `<start> → <now>` in local `HH:MM`, ahead of the zone, its start converted from status-last's UTC `Z` timestamp to the local zone (a small case under a non-UTC `TZ`) ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 61 | 21 | 42 | 5904 | 588428 | 78542 | 0.31 | 243 | unknown | 0/5 | nothing-left |  |  | full |
| Queue's snapshot line also shows the snapshot's `fetched_at` time, converted from UTC to local `HH:MM` (e.g. `snapshot 2h 3m old, fetched 09:52`) (a small case under a non-UTC `TZ`) ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 88 | 30 | 58 | 8692 | 834251 | 93608 | 0.40 | 299 | unknown | 1/5 | nothing-left |  |  | full |
| The unit fakes of `git tag` in `skills/tdd/scripts/tests/py/unit/test_status_report.py` and `skills/tdd/scripts/tests/py/unit/test_status_report_blocked.py` answer by the `--format` they are given, and the Landed pin in `test_status_report.py` asserts each line's tag name and subject, in order, rather than the exact line; no production change ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 22 | 44 | 6745 | 795377 | 42217 | 0.25 | 196 | n/a | n/a | n/a |  |  | full |
| Each Landed line shows its tag's `creatordate`, converted from the tagger's offset to the local zone as `YYYY-MM-DD HH:MM`, between the tag name and its subject (a case with a tag whose tagger offset differs from the local `TZ`) ⟦criterion 2⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 189 | 47 | 90 | 15307 | 1326613 | 137425 | 0.63 | 499 | unknown | 0/5 | nothing-left |  |  | full |
| No line of `status.sh --report` shows two zones side by side: with a status-last, a snapshot and a tag, under a non-UTC `TZ`, the zone name and UTC offset appear on the first line only and no shown time carries a `Z` or an offset of its own ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 52 | 12 | 24 | 4811 | 400270 | 37860 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| `.tdd/status-last` stores its time as a UTC ISO 8601 timestamp ending in `Z` when the report runs under a non-UTC `TZ` (a small case under `TZ=America/Chicago`) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 13 | 26 | 5675 | 399559 | 36429 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| The first line of `status.sh --report` names the machine's local zone once, with its UTC offset, e.g. `CST (UTC−6)` under `TZ=America/Chicago` on a winter date (a small case, in-process, no git) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| When `.tdd/status-last` exists, the report's first line opens with the window `<start> → <now>` in local `HH:MM`, ahead of the zone, its start converted from status-last's UTC `Z` timestamp to the local zone (a small case under a non-UTC `TZ`) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.04 |
| Queue's snapshot line also shows the snapshot's `fetched_at` time, converted from UTC to local `HH:MM` (e.g. `snapshot 2h 3m old, fetched 09:52`) (a small case under a non-UTC `TZ`) ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 51 | 0.12 |
| Each Landed line shows its tag's `creatordate`, converted from the tagger's offset to the local zone as `YYYY-MM-DD HH:MM`, between the tag name and its subject (a case with a tag whose tagger offset differs from the local `TZ`) ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.06 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 1 | 1 | 2 | 0 | 2 | 2 | 1 | 2 | 3 | 1 | 1 | 2 | 2 | 2 | 3 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 23 | 19 | 18 | 18 | 19 | 19 | 18 | 19 | 19 | 20 | 21 | 19 | 19 | 19 | 20 | 19 | 21 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 0 | 0 | 1 | 2 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 2 | 1 | 2 | 1 | 1 | 2 | 1 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 193 | 376 | 61667 | 5613405 | 616601 | 2.72 |
