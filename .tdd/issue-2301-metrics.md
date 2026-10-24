### 📊 Metrics — issue 2301

Wall time for the issue: 974 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2327.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.10 over 44 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90413 |
| 2 | $0.03 | 91378 |
| 3 | $0.04 | 93472 |
| 4 | $0.02 | 93824 |
| 5 | $0.02 | 94141 |
| 6 | $0.02 | 94460 |
| 7 | $0.02 | 95025 |
| 8 | $0.03 | 96426 |
| 9 | $0.03 | 97455 |
| 10 | $0.09 | 106521 |
| 11 | $0.04 | 108883 |
| 12 | $0.02 | 109182 |
| 13 | $0.03 | 109893 |
| 14 | $0.03 | 110467 |
| 15 | $0.03 | 111138 |
| 16 | $0.03 | 111859 |
| 17 | $0.09 | 119899 |
| 18 | $0.03 | 120928 |
| 19 | $0.03 | 121592 |
| 20 | $0.03 | 122592 |
| 21 | $0.03 | 123448 |
| 22 | $0.04 | 125144 |
| 23 | $0.03 | 125756 |
| 24 | $0.04 | 127860 |
| 25 | $0.03 | 128444 |
| 26 | $0.04 | 129638 |
| 27 | $0.04 | 131301 |
| 28 | $0.04 | 132909 |
| 29 | $0.03 | 133771 |
| 30 | $0.04 | 134888 |
| 31 | $0.04 | 136128 |
| 32 | $0.03 | 136808 |
| 33 | $0.03 | 137639 |
| 34 | $0.04 | 138699 |
| 35 | $0.04 | 139840 |
| 36 | $0.03 | 140642 |
| 37 | $0.04 | 142709 |
| 38 | $0.03 | 143491 |
| 39 | $0.04 | 144731 |
| 40 | $0.04 | 145623 |
| 41 | $0.03 | 146085 |
| 42 | $0.03 | 146326 |
| 43 | $0.03 | 146662 |
| 44 | $0.03 | 147148 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 10 | 1 | 2 | 1213 | 17442 | 13948 | 0.05 |
| diff | 2 | 1 | 0 | 0 | 74 | 36 | 11 | 22 | 4385 | 320249 | 36420 | 0.17 |
| red | 5 | 3 | 0 | 0 | 90 | 70 | 21 | 42 | 8261 | 623816 | 94234 | 0.38 |
| green | 5 | 2 | 0 | 0 | 161 | 73 | 31 | 52 | 8529 | 785694 | 87469 | 0.38 |
| red-contradicted | 1 | 0 | 0 | 0 | 22 | 18 | 5 | 10 | 2416 | 155709 | 19217 | 0.09 |
| refactor | 2 | 0 | 0 | 0 | 14 | 10 | 5 | 10 | 764 | 128511 | 29064 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 155 | 77 | 24 | 48 | 8413 | 641985 | 108212 | 0.42 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 218 | 140 | 50 | 90 | 17155 | 1389436 | 172140 | 0.74 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| red-contradicted | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Test-only, no production change: the four older #2030 cases in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py whose fake gh lists the calls it answers also answer a repository label lookup, `gh api repos/{owner}/{repo}/labels/<url-quoted name>` (a 200 when their scenario's repository holds the label, a 404 "Not Found" when it does not; in the no-answer case the lookup reports the label absent when the create is the call left unanswered, so that case still reaches the create), keeping every case green against the unchanged code ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 11 | 22 | 4385 | 320249 | 36420 | 0.17 | 106 | n/a | n/a | n/a |  |  | full |
| When the repository already holds the taken:<lane> label (the label lookup answers 200), a claim by unlabel_issue.main makes no `gh label create` call and no label-update call, and only adds the label to the issue; pinned by a small in-process case with gh faked at the subprocess boundary github.py calls through, recording every call made ⟦criterion 1⟧ | 8 | 3 | 0 | 0 | 0 | 0 | 96 | 37 | 66 | 11389 | 970250 | 141942 | 0.57 | 282 | unknown | 0/5 | nothing-left |  |  | full |
| When the repository lacks the taken:<lane> label (the label lookup answers 404), a claim by unlabel_issue.main creates it exactly once, with a fixed --color and a fixed --description and without --force, before adding it to the issue; a lookup gh gets no answer to exits 2 naming the taken label and the issue; pinned by small in-process cases with gh faked at the subprocess boundary github.py calls through, recording every call made ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 75 | 25 | 48 | 8581 | 723480 | 88042 | 0.38 | 194 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When the repository already holds the taken:<lane> label (the label lookup answers 200), a claim by unlabel_issue.main makes no `gh label create` call and no label-update call, and only adds the label to the issue; pinned by a small in-process case with gh faked at the subprocess boundary github.py calls through, recording every call made ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| When the repository lacks the taken:<lane> label (the label lookup answers 404), a claim by unlabel_issue.main creates it exactly once, with a fixed --color and a fixed --description and without --force, before adding it to the issue; a lookup gh gets no answer to exits 2 naming the taken label and the issue; pinned by small in-process cases with gh faked at the subprocess boundary github.py calls through, recording every call made ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 16 | 16 | 16 | 16 | 16 | 16 |  |  |  |  |  |  |
| affected | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 3 |
| target | 1 | 1 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 74 | 138 | 25568 | 2031421 | 280352 | 1.16 |
