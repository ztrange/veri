### 📊 Metrics — issue 2557

Wall time for the issue: 2123 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2595.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.06 over 48 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 89243 tokens, largest 136737 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 89243 |
| 2 | $0.03 | 91094 |
| 3 | $0.03 | 92654 |
| 4 | $0.02 | 93193 |
| 5 | $0.02 | 93967 |
| 6 | $0.02 | 94276 |
| 7 | $0.02 | 94553 |
| 8 | $0.02 | 94775 |
| 9 | $0.02 | 95347 |
| 10 | $0.03 | 96499 |
| 11 | $0.09 | 104767 |
| 12 | $0.03 | 106085 |
| 13 | $0.03 | 106934 |
| 14 | $0.03 | 107442 |
| 15 | $0.03 | 108280 |
| 16 | $0.03 | 109504 |
| 17 | $0.03 | 110507 |
| 18 | $0.03 | 111399 |
| 19 | $0.03 | 112092 |
| 20 | $0.03 | 113097 |
| 21 | $0.03 | 114468 |
| 22 | $0.03 | 115128 |
| 23 | $0.03 | 115844 |
| 24 | $0.03 | 116516 |
| 25 | $0.03 | 117195 |
| 26 | $0.04 | 118781 |
| 27 | $0.03 | 119197 |
| 28 | $0.04 | 121320 |
| 29 | $0.04 | 123729 |
| 30 | $0.03 | 124398 |
| 31 | $0.03 | 124624 |
| 32 | $0.03 | 125264 |
| 33 | $0.04 | 127539 |
| 34 | $0.03 | 128261 |
| 35 | $0.03 | 128708 |
| 36 | $0.05 | 131257 |
| 37 | $0.03 | 131977 |
| 38 | $0.03 | 132696 |
| 39 | $0.03 | 132926 |
| 40 | $0.03 | 133112 |
| 41 | $0.03 | 133568 |
| 42 | $0.03 | 134169 |
| 43 | $0.03 | 134765 |
| 44 | $0.03 | 135342 |
| 45 | $0.03 | 135859 |
| 46 | $0.03 | 136126 |
| 47 | $0.03 | 136447 |
| 48 | $0.03 | 136737 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 1 | 2 | 1230 | 0 | 33048 | 0.09 |
| red | 5 | 1 | 0 | 0 | 114 | 78 | 24 | 42 | 8575 | 618923 | 112844 | 0.43 |
| green | 2 | 1 | 0 | 0 | 92 | 25 | 9 | 16 | 2131 | 227525 | 30991 | 0.12 |
| refactor | 1 | 0 | 0 | 0 | 6 | 3 | 2 | 4 | 155 | 49790 | 14993 | 0.04 |
| pin | 3 | 3 | 0 | 0 | 57 | 29 | 9 | 18 | 2823 | 239431 | 47553 | 0.17 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 125 | 55 | 16 | 32 | 5755 | 399274 | 112006 | 0.38 |
| developer | claude-sonnet-5-5 | 6 | 0 | 0 | 0 | 156 | 90 | 29 | 50 | 9159 | 736395 | 127423 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| preflight-refused.sh called with an empty <issue-number> (argv "" and a non-empty <check>) exits 2 printing the usage line on stderr, writes no preflight-refused event anywhere under the main checkout and attempts no issue comment (in-process case in tests/py/unit/test_preflight_refused.py, failing on the current code) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 46 | 20 | 34 | 4669 | 461848 | 98985 | 0.34 | 248 | unknown | 0/5 | nothing-left |  |  | full |
| preflight-refused.sh with a missing or empty <check> (argv [], ["7"], ["7", ""]) still exits 2 printing only the usage line, writing no event and attempting no comment (pinned by an in-process case) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 8 | 16 | 2936 | 235196 | 34812 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| preflight-refused.sh with both a non-empty <issue-number> and <check> still writes exactly one preflight-refused event to .tdd/wt/<n>/.tdd/events.jsonl and posts exactly one issue comment on issue <n> (pinned by an in-process case) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 10 | 18 | 3126 | 270865 | 35434 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| No argument combination of preflight-refused.sh (missing, empty or both given) creates a .tdd/wt/.tdd/ directory under the main checkout, and a recorded refusal's event log lives in the run directory named after the issue, .tdd/wt/<n>/ (pinned by an in-process case) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 6 | 12 | 2953 | 167760 | 37150 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| preflight-refused.sh called with an empty <issue-number> (argv "" and a non-empty <check>) exits 2 printing the usage line on stderr, writes no preflight-refused event anywhere under the main checkout and attempts no issue comment (in-process case in tests/py/unit/test_preflight_refused.py, failing on the current code) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 3 | 3 | 2 | 2 | 2 | 2 |  |
| fast | 24 | 24 |  |  |  |  |  |
| target | 2 | 2 | 2 | 3 | 3 | 3 | 3 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 45 | 82 | 14914 | 1135669 | 239429 | 2.92 (estimate) |
