### 📊 Metrics — issue 1114

Wall time for the issue: 4293 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 8 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1119.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 17 | 2 | 4 | 1580 | 64194 | 43348 | 0.39 |
| diff | 4 | 2 | 0 | 0 | 488 | 109 | 26 | 52 | 9098 | 1305528 | 195689 | 2.01 |
| red | 7 | 1 | 0 | 0 | 591 | 256 | 52 | 94 | 25879 | 2472264 | 367082 | 3.95 |
| green | 2 | 1 | 0 | 0 | 180 | 47 | 15 | 28 | 4782 | 684058 | 90658 | 0.96 |
| refactor | 2 | 1 | 0 | 0 | 113 | 43 | 15 | 30 | 4496 | 764570 | 95021 | 1.00 |
| pin | 5 | 5 | 0 | 0 | 425 | 102 | 23 | 46 | 10175 | 1020549 | 223803 | 2.20 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 11 | 11 | 0 | 0 | 972 | 252 | 60 | 118 | 23224 | 2725313 | 497353 | 4.99 |
| developer | claude-opus-5-5 | 10 | 0 | 0 | 0 | 847 | 322 | 73 | 136 | 32786 | 3585850 | 518248 | 5.52 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| the existing cases that pin GraphQL-first set VERI_GH_DRIVER=auto themselves: every case in tests/py/test_capture_spec.py whose fake answers `gh issue view` or whose asserted call list starts with it sets the variable to auto with monkeypatch, and capture-spec.test.sh runs capture-spec.sh under VERI_GH_DRIVER=auto, with no other assertion changed, so today's GraphQL-then-REST behaviour stays pinned byte-identical under auto ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 55 | 13 | 26 | 4376 | 668982 | 100049 | 1.02 | 205 | n/a | n/a | n/a |  |  | full |
| with VERI_GH_DRIVER unset or set to rest, capture_spec.main reads the issue's labels and body through `gh api` only, starting no `gh issue view`, and prints the same spec ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 150 | 43 | 82 | 14616 | 2046152 | 286175 | 2.99 | 449 | unknown | 1/5 | nothing-structural |  |  | full |
| with VERI_GH_DRIVER=graphql, capture_spec.main reads the issue through `gh issue view` only, and a GraphQL failure is exit 2 with nothing on stdout and no `gh api` call ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 10 | 18 | 5514 | 424062 | 97920 | 0.98 | unknown | unknown | unknown | unknown |  |  | pin |
| with VERI_GH_DRIVER empty or any value other than auto, rest or graphql, capture_spec.main exits 2 with nothing on stdout, a stderr line naming VERI_GH_DRIVER and the value, and no gh process started ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 11 | 20 | 5137 | 469359 | 93722 | 0.95 | unknown | unknown | unknown | unknown |  |  | pin |
| capture-spec.test.sh has a case running capture-spec.sh with VERI_GH_DRIVER unset against a stub gh answering `gh api repos/{owner}/{repo}/issues/<n>`, getting the spec on stdout and recording no `gh issue view` call ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 14 | 28 | 6300 | 729781 | 98693 | 1.06 | unknown | unknown | unknown | unknown |  |  | pin |
| capture-spec.test.sh has a case running capture-spec.sh with VERI_GH_DRIVER=graphql in which a failing `gh issue view` gives exit 2, nothing on stdout and no `gh api` call ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 11 | 20 | 6057 | 478393 | 95978 | 0.98 | unknown | unknown | unknown | unknown |  |  | pin |
| hermetic-suites.test.sh's ambient-VERI_GH_DRIVER case covers capture-spec.test.sh: an ambient VERI_GH_DRIVER of auto, rest or graphql gives it the same exit and stdout as a cleared run ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 78 | 16 | 30 | 7708 | 793694 | 104076 | 1.15 | unknown | unknown | unknown | unknown |  |  | pin |
| every case in tests/py/test_capture_spec.py that runs capture_spec.main sets or clears VERI_GH_DRIVER itself, so the pytest suite's result does not depend on the caller's shell ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 13 | 26 | 4722 | 636546 | 95640 | 0.99 | 330 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| with VERI_GH_DRIVER unset or set to rest, capture_spec.main reads the issue's labels and body through `gh api` only, starting no `gh issue view`, and prints the same spec ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 113 | 1.00 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 53 | 51 | 56 | 55 | 53 | 49 | 50 |  |  |  |  |  |  |  |  |  |  |
| affected | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 143 | 1 | 140 |
| target | 0 | 1 | 0 | 0 | 0 | 1 | 1 | 1 | 1 | 152 | 137 |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 133 | 254 | 56010 | 6311163 | 1015601 | 10.51 |
