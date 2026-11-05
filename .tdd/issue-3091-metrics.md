### 📊 Metrics — issue 3091

Wall time for the issue: 7917 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3093.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.14 over 91 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90493 tokens, largest 193399 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90493 |
| 2 | $0.07 | 97572 |
| 3 | $0.03 | 99028 |
| 4 | $0.04 | 100945 |
| 5 | $0.02 | 101387 |
| 6 | $0.02 | 101740 |
| 7 | $0.02 | 102059 |
| 8 | $0.02 | 102346 |
| 9 | $0.02 | 102600 |
| 10 | $0.02 | 102926 |
| 11 | $0.02 | 103206 |
| 12 | $0.03 | 104041 |
| 13 | $0.02 | 104358 |
| 14 | $0.02 | 104854 |
| 15 | $0.05 | 108867 |
| 16 | $0.04 | 111006 |
| 17 | $0.07 | 116621 |
| 18 | $0.04 | 119104 |
| 19 | $0.03 | 120096 |
| 20 | $0.03 | 120454 |
| 21 | $0.03 | 121205 |
| 22 | $0.03 | 121765 |
| 23 | $0.03 | 122497 |
| 24 | $0.03 | 123026 |
| 25 | $0.09 | 131579 |
| 26 | $0.03 | 132380 |
| 27 | $0.03 | 132567 |
| 28 | $0.03 | 133023 |
| 29 | $0.03 | 133636 |
| 30 | $0.03 | 134206 |
| 31 | $0.03 | 134748 |
| 32 | $0.03 | 135304 |
| 33 | $0.03 | 135998 |
| 34 | $0.03 | 136547 |
| 35 | $0.03 | 137216 |
| 36 | $0.04 | 138572 |
| 37 | $0.04 | 139929 |
| 38 | $0.03 | 140471 |
| 39 | $0.04 | 142479 |
| 40 | $0.04 | 143808 |
| 41 | $0.03 | 144451 |
| 42 | $0.03 | 145183 |
| 43 | $0.04 | 146724 |
| 44 | $0.04 | 147751 |
| 45 | $0.09 | 155907 |
| 46 | $0.04 | 157380 |
| 47 | $0.04 | 158140 |
| 48 | $0.05 | 159868 |
| 49 | $0.04 | 160934 |
| 50 | $0.03 | 161249 |
| 51 | $0.04 | 162423 |
| 52 | $0.04 | 163030 |
| 53 | $0.04 | 163729 |
| 54 | $0.05 | 165286 |
| 55 | $0.06 | 168762 |
| 56 | $0.04 | 169344 |
| 57 | $0.04 | 169829 |
| 58 | $0.04 | 170613 |
| 59 | $0.04 | 171461 |
| 60 | $0.04 | 171812 |
| 61 | $0.04 | 172526 |
| 62 | $0.04 | 173738 |
| 63 | $0.04 | 174695 |
| 64 | $0.04 | 175131 |
| 65 | $0.04 | 176284 |
| 66 | $0.04 | 176966 |
| 67 | $0.04 | 177815 |
| 68 | $0.04 | 178460 |
| 69 | $0.05 | 179715 |
| 70 | $0.04 | 180533 |
| 71 | $0.05 | 182167 |
| 72 | $0.05 | 183401 |
| 73 | $0.04 | 183736 |
| 74 | $0.05 | 185069 |
| 75 | $0.04 | 186016 |
| 76 | $0.04 | 186630 |
| 77 | $0.04 | 187408 |
| 78 | $0.04 | 187705 |
| 79 | $0.04 | 188303 |
| 80 | $0.04 | 188936 |
| 81 | $0.05 | 189946 |
| 82 | $0.04 | 190278 |
| 83 | $0.04 | 190495 |
| 84 | $0.04 | 190819 |
| 85 | $0.04 | 191287 |
| 86 | $0.04 | 191770 |
| 87 | $0.04 | 192038 |
| 88 | $0.04 | 192259 |
| 89 | $0.04 | 192630 |
| 90 | $0.04 | 192940 |
| 91 | $0.04 | 193399 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 13 | 1 | 2 | 1338 | 0 | 32123 | 0.09 |
| diff | 7 | 2 | 2 | 0 | 868 | 161 | 38 | 76 | 12987 | 1100998 | 175273 | 0.96 |
| red | 7 | 3 | 0 | 0 | 482 | 196 | 41 | 82 | 20670 | 1382955 | 207826 | 1.26 |
| green | 7 | 1 | 2 | 0 | 1047 | 168 | 42 | 80 | 13761 | 1271556 | 137566 | 0.76 |
| red-supersede | 1 | 0 | 0 | 0 | 63 | 48 | 8 | 16 | 5400 | 280051 | 25264 | 0.15 |
| pin | 2 | 1 | 1 | 0 | 69 | 34 | 6 | 12 | 2808 | 158741 | 32355 | 0.12 |
| red-missing | 1 | 0 | 0 | 0 | 60 | 38 | 5 | 10 | 3058 | 140940 | 39323 | 0.14 |
| refactor | 1 | 0 | 0 | 0 | 7 | 3 | 2 | 4 | 230 | 30978 | 33560 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 8 | 5 | 0 | 1307 | 224 | 46 | 90 | 16643 | 1203062 | 228118 | 0.86 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 251 | 151 | 31 | 60 | 13458 | 952184 | 162077 | 0.64 |
| developer | claude-opus-5-5 | 9 | 0 | 0 | 0 | 1053 | 286 | 66 | 132 | 30151 | 2210973 | 293095 | 2.08 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 1026 | 1.13 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1968 | 1.25 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| pin | 37 | 0.06 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Update the two older cases in skills/tdd/scripts/tests/py/unit/test_grade_prose.py that pin the follow-up being skipped or its exact stderr — 'test_with_no_verdict_retries_0_a_first_reply_leaving_out_one_requirement_id_launches_the_grader_once_and_exits_2_naming_it_missing_2215' and 'test_a_follow_up_reply_leaving_the_missing_requirement_id_out_again_makes_grade_prose_exit_2_naming_it_after_two_launches_and_append_no_grading_event_2215' — so each still asserts exit 2, A2 named as missing and no grading event, with a stub whose later replies grade no row, but no longer pins a launch count or the exact stderr line; a test-only change, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 32 | 8 | 16 | 2533 | 207896 | 51087 | 0.17 | 191 | n/a | n/a | n/a |  |  | full |
| With the VERI_NO_VERDICT_RETRIES relaunches spent — a stub grader (CLAUDE_BIN or the launch boundary) whose first full-unit reply breaks protocol and whose relaunch grades all of a 401-row unit's rows but a contiguous run — grade-prose.sh asks the grader again for the missing rows only, and when that follow-up grades them it exits 0 with PASS, a grade for every row ⟦criterion 1⟧ | 11 | 3 | 2 | 0 | 0 | 0 | 324 | 74 | 146 | 30708 | 2416903 | 268120 | 1.69 | unknown | diff 2/2, red 1/2 | unknown | unknown |  |  | pin |
| When the missing-rows follow-up asked after the relaunches are spent still leaves rows ungraded, grade-prose.sh exits 2 with a stderr line naming the missing requirement IDs and saying the follow-up for them was tried ⟦criterion 1⟧ | 13 | 3 | 3 | 0 | 0 | 0 | 292 | 60 | 118 | 25673 | 1741420 | 331960 | 1.61 | 1680 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When the missing-rows follow-up asked after the relaunches are spent still leaves rows ungraded, grade-prose.sh exits 2 with a stderr line naming the missing requirement IDs and saying the follow-up for them was tried ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 7 | 0.09 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 29 | 42 | 41 | 29 | 52 | 48 | 68 | 55 | 60 | 53 | 55 | 51 |  |  |  |  |  |  |  |  |  |  |
| affected | 3 | 6 | 5 | 9 | 4 | 3 | 67 | 93 | 74 | 8 | 11 | 10 | 10 | 12 | 72 | 8 | 9 | 9 | 4 | 6 | 81 | 95 |
| target | 2 | 3 | 3 | 3 | 7 | 8 | 6 | 4 | 7 | 7 | 5 | 6 | 5 | 5 | 4 | 6 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 143 | 282 | 60252 | 4366219 | 683290 | 7.71 (estimate) |
