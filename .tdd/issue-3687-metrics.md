### 📊 Metrics — issue 3687

Wall time for the issue: 2002 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3689.
Lane: ready-for-agent:mu
Suite flakes: skills/tdd/scripts/tests/py/test_supervise.py::test_cli_on_term_int_or_hup_writes_2_exits_2_and_leaves_no_leaf_while_an_ignored_int_lets_the_leaf_finish_with_its_own_0_and_wait_leaf_against_a_live_supervisor_exits_3_silently, skills/tdd/scripts/tests/py/test_supervise.py::test_cli_on_term_int_or_hup_writes_2_exits_2_and_leaves_no_leaf_while_an_ignored_int_lets_the_leaf_finish_with_its_own_0_and_wait_leaf_against_a_live_supervisor_exits_3_silently.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.48 over 118 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 80084 tokens, largest 152275 tokens
Conductor context: first turn 80102 tokens, largest 161916 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.51 | 80084 |
| 2 | $0.07 | 86758 |
| 3 | $0.04 | 88465 |
| 4 | $0.04 | 90430 |
| 5 | $0.03 | 90907 |
| 6 | $0.04 | 91546 |
| 7 | $0.02 | 91883 |
| 8 | $0.03 | 92219 |
| 9 | $0.04 | 92967 |
| 10 | $0.03 | 94486 |
| 11 | $0.07 | 99220 |
| 12 | $0.05 | 102159 |
| 13 | $0.04 | 103878 |
| 14 | $0.04 | 105240 |
| 15 | $0.04 | 105994 |
| 16 | $0.03 | 106307 |
| 17 | $0.03 | 106889 |
| 18 | $0.04 | 107629 |
| 19 | $0.04 | 109681 |
| 20 | $0.04 | 110638 |
| 21 | $0.03 | 110910 |
| 22 | $0.04 | 111440 |
| 23 | $0.03 | 111694 |
| 24 | $0.03 | 111881 |
| 25 | $0.03 | 112002 |
| 26 | $0.03 | 112225 |
| 27 | $0.04 | 113123 |
| 28 | $0.04 | 113755 |
| 29 | $0.03 | 114320 |
| 30 | $0.10 | 123433 |
| 31 | $0.04 | 124408 |
| 32 | $0.04 | 125012 |
| 33 | $0.04 | 125308 |
| 34 | $0.03 | 125605 |
| 35 | $0.04 | 125859 |
| 36 | $0.04 | 127011 |
| 37 | $0.04 | 127728 |
| 38 | $0.04 | 128453 |
| 39 | $0.04 | 129292 |
| 40 | $0.03 | 129580 |
| 41 | $0.04 | 129892 |
| 42 | $0.04 | 130478 |
| 43 | $0.04 | 131406 |
| 44 | $0.06 | 135140 |
| 45 | $0.04 | 135748 |
| 46 | $0.04 | 136498 |
| 47 | $0.05 | 137535 |
| 48 | $0.04 | 138376 |
| 49 | $0.04 | 139076 |
| 50 | $0.04 | 140188 |
| 51 | $0.04 | 140710 |
| 52 | $0.05 | 141775 |
| 53 | $0.11 | 150697 |
| 54 | $0.04 | 151023 |
| 55 | $0.04 | 152025 |
| 56 | $0.04 | 152275 |
| 57 | $0.50 | 80102 |
| 58 | $0.07 | 86559 |
| 59 | $0.03 | 88266 |
| 60 | $0.03 | 90215 |
| 61 | $0.03 | 91359 |
| 62 | $0.02 | 91844 |
| 63 | $0.02 | 92353 |
| 64 | $0.02 | 92678 |
| 65 | $0.02 | 92913 |
| 66 | $0.02 | 93463 |
| 67 | $0.02 | 93896 |
| 68 | $0.02 | 94564 |
| 69 | $0.05 | 99001 |
| 70 | $0.03 | 99760 |
| 71 | $0.02 | 100259 |
| 72 | $0.02 | 100823 |
| 73 | $0.02 | 101187 |
| 74 | $0.03 | 101875 |
| 75 | $0.10 | 111530 |
| 76 | $0.03 | 112348 |
| 77 | $0.03 | 113019 |
| 78 | $0.03 | 113677 |
| 79 | $0.03 | 114545 |
| 80 | $0.03 | 115192 |
| 81 | $0.03 | 116026 |
| 82 | $0.03 | 117207 |
| 83 | $0.03 | 118279 |
| 84 | $0.03 | 119115 |
| 85 | $0.03 | 120121 |
| 86 | $0.04 | 121557 |
| 87 | $0.03 | 122755 |
| 88 | $0.03 | 123582 |
| 89 | $0.04 | 124955 |
| 90 | $0.03 | 125766 |
| 91 | $0.04 | 127079 |
| 92 | $0.04 | 128396 |
| 93 | $0.03 | 129348 |
| 94 | $0.15 | 145152 |
| 95 | $0.03 | 145529 |
| 96 | $0.03 | 145965 |
| 97 | $0.03 | 146484 |
| 98 | $0.03 | 146853 |
| 99 | $0.03 | 147357 |
| 100 | $0.06 | 150702 |
| 101 | $0.04 | 151613 |
| 102 | $0.03 | 151969 |
| 103 | $0.03 | 152408 |
| 104 | $0.03 | 152781 |
| 105 | $0.04 | 153612 |
| 106 | $0.04 | 154354 |
| 107 | $0.04 | 155065 |
| 108 | $0.03 | 155549 |
| 109 | $0.03 | 155976 |
| 110 | $0.04 | 156622 |
| 111 | $0.04 | 157666 |
| 112 | $0.04 | 159001 |
| 113 | $0.04 | 159925 |
| 114 | $0.04 | 160764 |
| 115 | $0.04 | 161189 |
| 116 | $0.04 | 161618 |
| 117 | $0.03 | 161916 |

#### Conductor comments, by family

| family | turns | output tokens | dollars |
| --- | ---: | ---: | ---: |
| ✅ Step done | 0 | 0 | $0.00 |
| ✅ Done | 0 | 0 | $0.00 |
| 🔴 Red | 0 | 0 | $0.00 |
| 🟢 Green | 0 | 0 | $0.00 |
| 🛠️ Refactor | 0 | 0 | $0.00 |
| 🔎 verify-green | 0 | 0 | $0.00 |
| 🔎 verify-refactor | 0 | 0 | $0.00 |
| 🔎 verify-<phase> (revised) | 1 | 389 | $0.01 |
| 🗺️ Plan | 0 | 0 | $0.00 |
| 🗺️ verify-plan | 0 | 0 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 1 | 389 | $0.01 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 2 | 0 | 0 | 22 | 17 | 3 | 6 | 1746 | 30810 | 31878 | 0.10 |
| red | 9 | 4 | 0 | 0 | 233 | 155 | 44 | 88 | 15456 | 888809 | 179252 | 0.69 |
| green | 12 | 4 | 2 | 0 | 629 | 180 | 55 | 104 | 15400 | 885181 | 169466 | 0.80 |
| refactor | 4 | 0 | 0 | 0 | 33 | 24 | 10 | 20 | 1434 | 138654 | 57645 | 0.17 |
| pin | 1 | 1 | 0 | 0 | 15 | 8 | 2 | 4 | 768 | 23514 | 14385 | 0.05 |
| predicate | 4 | 0 | 0 | 0 | 38 | 26 | 11 | 22 | 1836 | 144359 | 48573 | 0.15 |
| cover | 2 | 0 | 0 | 0 | 40 | 28 | 13 | 22 | 2504 | 178075 | 28420 | 0.11 |
| structural | 2 | 0 | 0 | 0 | 40 | 30 | 10 | 20 | 3224 | 163559 | 29951 | 0.12 |
| transform | 2 | 2 | 0 | 0 | 30 | 22 | 8 | 16 | 1540 | 115729 | 26101 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 13 | 2 | 0 | 628 | 183 | 56 | 112 | 15123 | 893812 | 201912 | 0.75 |
| developer | claude-sonnet-5-5 | 20 | 0 | 0 | 0 | 366 | 256 | 88 | 166 | 24637 | 1481464 | 330646 | 1.22 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 86 | 51 | 12 | 24 | 4148 | 193414 | 53113 | 0.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 658 | 0.67 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `release-issue.sh` on an issue labelled only `taken:<lane>` whose comment starts `### ⛔ Preflight refused`, driven through the real REST adapter of `github.py` with only the gh process boundary faked by a fixture (the issue's labels, and its comments at `issues/<n>/comments`), exits 0 and swaps `taken:<lane>` for the opt-in label (fails on current code with exit 3; a small case, no real process) ⟦criterion 3⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 152 | 42 | 84 | 14142 | 793644 | 135762 | 0.69 | 638 | 2/2 | 0/5 | nothing-left |  |  | full |
| The REST adapter's `issue_view(n, "comments")` returns the comment bodies of every page of `issues/<n>/comments`: a fixture of two pages with the `### ⛔ Preflight refused` comment on page 2 has that comment's body in the answer ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 9 | 18 | 3339 | 180061 | 36161 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| The graphql adapter's `issue_view(n, "comments")` returns the issue's comment bodies of every page, not its label names: two pages, the `### ⛔ Preflight refused` comment on page 2, in the answer ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 67 | 22 | 40 | 5707 | 342647 | 88232 | 0.31 | 597 | unknown | 0/5 | nothing-left |  |  | full |
| The REST adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the issue body ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 55 | 19 | 36 | 5035 | 288747 | 78589 | 0.28 | 312 | unknown | 0/5 | nothing-left |  |  | full |
| The graphql adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the label names ⟦criterion 2⟧ | 15 | 4 | 0 | 0 | 0 | 0 | 168 | 61 | 118 | 13939 | 932781 | 215049 | 0.77 | 254 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `release-issue.sh` on an issue labelled only `taken:<lane>` whose comment starts `### ⛔ Preflight refused`, driven through the real REST adapter of `github.py` with only the gh process boundary faked by a fixture (the issue's labels, and its comments at `issues/<n>/comments`), exits 0 and swaps `taken:<lane>` for the opt-in label (fails on current code with exit 3; a small case, no real process) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.05 |
| The graphql adapter's `issue_view(n, "comments")` returns the issue's comment bodies of every page, not its label names: two pages, the `### ⛔ Preflight refused` comment on page 2, in the answer ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.04 |
| The REST adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the issue body ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| The graphql adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the label names ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 2/10 | candidates-done |

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| `release-issue.sh` on an issue labelled only `taken:<lane>` whose comment starts `### ⛔ Preflight refused`, driven through the real REST adapter of `github.py` with only the gh process boundary faked by a fixture (the issue's labels, and its comments at `issues/<n>/comments`), exits 0 and swaps `taken:<lane>` for the opt-in label (fails on current code with exit 3; a small case, no real process) ⟦criterion 3⟧ | 1 | 0 | 1 | nothing-left 1 |
| The graphql adapter's `issue_view(n, "comments")` returns the issue's comment bodies of every page, not its label names: two pages, the `### ⛔ Preflight refused` comment on page 2, in the answer ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| The REST adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the issue body ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| The graphql adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the label names ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 5 | 2 | 4 | candidates-done 1, nothing-left 4 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 2 | 4 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 2 | 2 | 3 | 4 | 2 | 1 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 8 | 9 | 7 | 6 | 7 | 6 | 7 | 6 | 10 | 23 | 8 | 11 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 2 | 3 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 156 | 302 | 43908 | 2568690 | 585671 | 7.77 (estimate) |
