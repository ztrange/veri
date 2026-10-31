### 📊 Metrics — issue 2700

Wall time for the issue: 6553 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 10 of 10 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2735.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.27 over 56 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86642 tokens, largest 203987 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86642 |
| 2 | $0.09 | 96160 |
| 3 | $0.04 | 98172 |
| 4 | $0.03 | 99147 |
| 5 | $0.02 | 99517 |
| 6 | $0.02 | 99820 |
| 7 | $0.02 | 100075 |
| 8 | $0.02 | 100471 |
| 9 | $0.05 | 104604 |
| 10 | $0.10 | 114320 |
| 11 | $0.06 | 118689 |
| 12 | $0.12 | 131175 |
| 13 | $0.04 | 133183 |
| 14 | $0.04 | 134752 |
| 15 | $0.03 | 135615 |
| 16 | $0.04 | 137335 |
| 17 | $0.04 | 138341 |
| 18 | $0.10 | 147163 |
| 19 | $0.05 | 149613 |
| 20 | $0.04 | 150424 |
| 21 | $0.05 | 152386 |
| 22 | $0.04 | 153194 |
| 23 | $0.04 | 154609 |
| 24 | $0.05 | 157202 |
| 25 | $0.05 | 160107 |
| 26 | $0.06 | 163370 |
| 27 | $0.06 | 167127 |
| 28 | $0.05 | 169266 |
| 29 | $0.04 | 170457 |
| 30 | $0.05 | 172742 |
| 31 | $0.04 | 173807 |
| 32 | $0.05 | 175289 |
| 33 | $0.04 | 176286 |
| 34 | $0.04 | 176732 |
| 35 | $0.04 | 177899 |
| 36 | $0.05 | 179367 |
| 37 | $0.06 | 182044 |
| 38 | $0.06 | 185067 |
| 39 | $0.05 | 186342 |
| 40 | $0.05 | 187862 |
| 41 | $0.04 | 188260 |
| 42 | $0.06 | 190455 |
| 43 | $0.05 | 192332 |
| 44 | $0.05 | 193434 |
| 45 | $0.05 | 195268 |
| 46 | $0.05 | 197169 |
| 47 | $0.05 | 198763 |
| 48 | $0.05 | 200360 |
| 49 | $0.05 | 201311 |
| 50 | $0.04 | 201613 |
| 51 | $0.04 | 201835 |
| 52 | $0.04 | 202258 |
| 53 | $0.05 | 202894 |
| 54 | $0.04 | 203160 |
| 55 | $0.04 | 203410 |
| 56 | $0.05 | 203987 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 9 | 1 | 2 | 1116 | 0 | 32879 | 0.09 |
| red | 18 | 7 | 0 | 0 | 627 | 294 | 91 | 174 | 30234 | 2702467 | 381783 | 1.63 |
| green | 22 | 7 | 4 | 0 | 1629 | 409 | 125 | 234 | 40975 | 3596421 | 406595 | 2.34 |
| refactor | 9 | 2 | 0 | 0 | 185 | 80 | 34 | 68 | 6848 | 956879 | 168426 | 0.59 |
| pin | 3 | 3 | 0 | 0 | 80 | 36 | 13 | 26 | 3693 | 373547 | 53016 | 0.21 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 24 | 20 | 4 | 0 | 1364 | 338 | 105 | 204 | 30763 | 2931832 | 361685 | 1.51 |
| developer | claude-sonnet-5-5 | 20 | 0 | 0 | 0 | 567 | 286 | 104 | 206 | 30187 | 3225531 | 433950 | 1.71 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 601 | 204 | 55 | 94 | 21916 | 1471951 | 247064 | 1.64 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1329 | 2.12 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| status.sh text lists a run with a worktree and an events.jsonl but no ledger whose only event is preflight-refused, as a line naming its issue number (the run directory's name) and `refused <check>` ⟦criterion 1⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 142 | 47 | 80 | 14721 | 1191984 | 196302 | 1.00 | 784 | 2/2 | 0/5 | nothing-left |  |  | full |
| status.sh text lists a run with no ledger, an events.jsonl holding no launch and no end mark, and a live conductor, as a line naming its issue number and `running` ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 66 | 26 | 48 | 6642 | 735333 | 90941 | 0.37 | 312 | unknown | 0/5 | nothing-left |  |  | full |
| status.sh --json never counts a run in the scope totals that it does not list: a run with no ledger whose run_activity returns None, an empty events.jsonl with no live conductor, is either both listed and counted or neither ⟦added⟧ ⟦criterion 3⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 117 | 33 | 62 | 11569 | 931993 | 131174 | 0.68 | 475 | 1/2 | 0/5 | nothing-left |  |  | full |
| status.sh text shows `running` for a run with no ledger and a live conductor whose events.jsonl holds only a preflight-refused event from an earlier launch, the relaunch the issue observed for run 1059 ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 85 | 28 | 56 | 8122 | 831962 | 106782 | 0.43 | 381 | unknown | 1/5 | nothing-left |  |  | full |
| status.sh text lists a run with no ledger, an events.jsonl holding no launch and no end mark, and no live conductor, as `stale` rather than omitting it | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 10 | 20 | 3095 | 308948 | 40483 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| status.sh text lists a run with no ledger, a live conductor and an empty events.jsonl as `running`, with exit 0 and no traceback | 8 | 3 | 1 | 0 | 0 | 0 | 141 | 45 | 90 | 14586 | 1397887 | 157155 | 0.85 | 541 | 1/2 | 1/5 | nothing-left |  |  | full |
| status.sh --json includes a run with no ledger whose only event is preflight-refused, with `issue` its run directory's name, `state` `refused`, and `step` and `title` both empty ⟦criterion 2⟧ | 6 | 2 | 0 | 0 | 0 | 0 | 104 | 29 | 56 | 9192 | 850587 | 114292 | 0.56 | 338 | 1/2 | 0/5 | nothing-left |  |  | full |
| status.sh --json includes a run with no ledger, an events.jsonl holding no launch and no end mark, and a live conductor, with `issue` its run directory's name, `state` `running`, and `step` and `title` both empty ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 11 | 22 | 3319 | 341770 | 37384 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| The scope totals' `attempted` counts a run with no ledger exactly once and the run is listed, so with one ledger run and one ledger-less refused run both the listed lines and `attempted` say 2 ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 9 | 18 | 3641 | 276309 | 41771 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| The scope totals' `attempted` counts a listed run that has a ledger and no events.jsonl, so `attempted` equals the runs listed for it too; a run whose events vanish after render read them stays out of the totals as test_main_json_leaves_a_run_out_of_the_scope_totals_when_its_events_vanish_after_render_read_them_2559 pins ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 74 | 25 | 50 | 6863 | 762541 | 93536 | 0.38 | 299 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| status.sh text lists a run with a worktree and an events.jsonl but no ledger whose only event is preflight-refused, as a line naming its issue number (the run directory's name) and `refused <check>` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.09 |
| status.sh text lists a run with no ledger, an events.jsonl holding no launch and no end mark, and a live conductor, as a line naming its issue number and `running` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.06 |
| status.sh --json never counts a run in the scope totals that it does not list: a run with no ledger whose run_activity returns None, an empty events.jsonl with no live conductor, is either both listed and counted or neither ⟦added⟧ ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.05 |
| status.sh text shows `running` for a run with no ledger and a live conductor whose events.jsonl holds only a preflight-refused event from an earlier launch, the relaunch the issue observed for run 1059 ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 65 | 0.13 |
| status.sh text lists a run with no ledger, a live conductor and an empty events.jsonl as `running`, with exit 0 and no traceback | 1 | 1/5 | nothing-left | PASS | 0 | 75 | 0.15 |
| status.sh --json includes a run with no ledger whose only event is preflight-refused, with `issue` its run directory's name, `state` `refused`, and `step` and `title` both empty ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.06 |
| The scope totals' `attempted` counts a listed run that has a ledger and no events.jsonl, so `attempted` equals the runs listed for it too; a run whose events vanish after render read them stays out of the totals as test_main_json_leaves_a_run_out_of_the_scope_totals_when_its_events_vanish_after_render_read_them_2559 pins ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 4 | 6 | 4 | 0 | 4 | 4 | 5 | 6 | 7 | 6 | 3 | 0 | 4 | 4 | 4 | 4 | 6 | 7 | 0 | 6 | 4 | 3 | 3 | 3 | 43 | 3 | 0 | 4 | 3 | 4 | 4 | 0 | 5 | 6 | 0 | 6 | 5 | 6 | 4 | 3 | 3 | 3 | 6 | 0 | 5 | 4 | 3 | 3 | 3 | 6 | 4 | 7 |
| fast | 31 | 28 | 26 | 26 | 26 | 35 | 33 | 33 | 25 | 25 | 32 | 34 | 33 | 25 | 26 | 26 | 25 | 27 | 28 | 28 | 30 | 23 | 28 | 28 | 26 | 30 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 4 | 3 | 4 | 3 | 4 | 3 | 3 | 3 | 3 | 4 | 6 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 4 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 264 | 504 | 82866 | 7629314 | 1042699 | 8.13 (estimate) |
