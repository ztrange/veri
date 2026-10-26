### 📊 Metrics — issue 2420

Wall time for the issue: 1319 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2423.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.69 over 41 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 87766 tokens, largest 121774 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 87766 |
| 2 | $0.03 | 89801 |
| 3 | $0.03 | 91738 |
| 4 | $0.02 | 92076 |
| 5 | $0.02 | 92448 |
| 6 | $0.02 | 93022 |
| 7 | $0.02 | 93589 |
| 8 | $0.02 | 94214 |
| 9 | $0.03 | 95334 |
| 10 | $0.02 | 95614 |
| 11 | $0.03 | 96841 |
| 12 | $0.03 | 97772 |
| 13 | $0.02 | 98322 |
| 14 | $0.03 | 99006 |
| 15 | $0.02 | 99519 |
| 16 | $0.03 | 100920 |
| 17 | $0.03 | 101666 |
| 18 | $0.03 | 102620 |
| 19 | $0.03 | 103432 |
| 20 | $0.03 | 104266 |
| 21 | $0.03 | 105457 |
| 22 | $0.03 | 106383 |
| 23 | $0.03 | 107281 |
| 24 | $0.03 | 108011 |
| 25 | $0.02 | 108424 |
| 26 | $0.03 | 109450 |
| 27 | $0.03 | 109930 |
| 28 | $0.04 | 111757 |
| 29 | $0.04 | 114197 |
| 30 | $0.03 | 114962 |
| 31 | $0.03 | 115344 |
| 32 | $0.03 | 116133 |
| 33 | $0.04 | 117763 |
| 34 | $0.03 | 118571 |
| 35 | $0.03 | 119447 |
| 36 | $0.03 | 119746 |
| 37 | $0.03 | 120110 |
| 38 | $0.03 | 120666 |
| 39 | $0.03 | 120993 |
| 40 | $0.03 | 121430 |
| 41 | $0.03 | 121774 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 7 | 5 | 1 | 2 | 617 | 0 | 32407 | 0.09 |
| red | 4 | 1 | 0 | 0 | 68 | 49 | 17 | 32 | 6097 | 457022 | 89795 | 0.33 |
| green | 2 | 1 | 0 | 0 | 75 | 25 | 11 | 20 | 2484 | 290155 | 31042 | 0.13 |
| refactor | 1 | 0 | 0 | 0 | 6 | 3 | 3 | 4 | 262 | 49442 | 15616 | 0.05 |
| pin | 2 | 2 | 0 | 0 | 27 | 16 | 6 | 12 | 1728 | 157035 | 30137 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 5 | 5 | 0 | 0 | 85 | 41 | 16 | 30 | 4273 | 379900 | 93769 | 0.32 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 98 | 57 | 22 | 40 | 6915 | 573754 | 105228 | 0.39 |

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
| With the gh listing faked so one entry, a pull request labelled parked with no parked comment, carries a pull_request key, and another is an issue labelled parked with a well-formed parked comment, parked-issues.sh writes only the issue's number, title, Cause and Unblock row to stdout and exits 0, writing nothing about the pull request (a small in-process case in tests/py/unit/test_parked_issues.py, faking only the gh boundary) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 55 | 25 | 44 | 5866 | 628966 | 100992 | 0.37 | 218 | unknown | 0/5 | nothing-left |  |  | full |
| An issue labelled parked with no parked comment, listed beside a parked pull request, still makes parked-issues.sh exit 2 with "parked-issues.sh: issue #<n> has no parked comment" on stderr, so the guard is kept (a small in-process case in tests/py/unit/test_parked_issues.py) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 6 | 12 | 2418 | 162277 | 33039 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| With the gh listing faked to hold only pull requests labelled parked and no issue, parked-issues.sh exits 3 and writes nothing to stdout, nothing being parked (a small in-process case in tests/py/unit/test_parked_issues.py) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 6 | 12 | 2287 | 162411 | 32559 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With the gh listing faked so one entry, a pull request labelled parked with no parked comment, carries a pull_request key, and another is an issue labelled parked with a well-formed parked comment, parked-issues.sh writes only the issue's number, title, Cause and Unblock row to stdout and exits 0, writing nothing about the pull request (a small in-process case in tests/py/unit/test_parked_issues.py, faking only the gh boundary) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 1 | 1 | 1 | 1 |
| fast | 19 | 17 |  |  |  |  |  |
| target | 0 | 1 | 1 | 1 | 1 | 1 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 38 | 70 | 11188 | 953654 | 198997 | 0.70 |
