### 📊 Metrics — issue 3687

Wall time for the issue: 560 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3689.
Lane: ready-for-agent:mu
Suite flakes: skills/tdd/scripts/tests/py/test_supervise.py::test_cli_on_term_int_or_hup_writes_2_exits_2_and_leaves_no_leaf_while_an_ignored_int_lets_the_leaf_finish_with_its_own_0_and_wait_leaf_against_a_live_supervisor_exits_3_silently, skills/tdd/scripts/tests/py/test_supervise.py::test_cli_on_term_int_or_hup_writes_2_exits_2_and_leaves_no_leaf_while_an_ignored_int_lets_the_leaf_finish_with_its_own_0_and_wait_leaf_against_a_live_supervisor_exits_3_silently.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $10.57 over 211 turns, in 4 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 80084 tokens, largest 152275 tokens
Conductor context: first turn 80102 tokens, largest 165872 tokens
Conductor context: first turn 80228 tokens, largest 149380 tokens
Conductor context: first turn 80226 tokens, largest 133030 tokens
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
| 57 | $0.51 | 80102 |
| 58 | $0.08 | 86559 |
| 59 | $0.04 | 88266 |
| 60 | $0.04 | 90215 |
| 61 | $0.04 | 91359 |
| 62 | $0.03 | 91844 |
| 63 | $0.03 | 92353 |
| 64 | $0.03 | 92678 |
| 65 | $0.03 | 92913 |
| 66 | $0.04 | 93463 |
| 67 | $0.03 | 93896 |
| 68 | $0.03 | 94564 |
| 69 | $0.07 | 99001 |
| 70 | $0.03 | 99760 |
| 71 | $0.03 | 100259 |
| 72 | $0.04 | 100823 |
| 73 | $0.03 | 101187 |
| 74 | $0.04 | 101875 |
| 75 | $0.10 | 111530 |
| 76 | $0.04 | 112348 |
| 77 | $0.04 | 113019 |
| 78 | $0.04 | 113677 |
| 79 | $0.04 | 114545 |
| 80 | $0.04 | 115192 |
| 81 | $0.04 | 116026 |
| 82 | $0.04 | 117207 |
| 83 | $0.04 | 118279 |
| 84 | $0.04 | 119115 |
| 85 | $0.04 | 120121 |
| 86 | $0.05 | 121557 |
| 87 | $0.04 | 122755 |
| 88 | $0.04 | 123582 |
| 89 | $0.05 | 124955 |
| 90 | $0.04 | 125766 |
| 91 | $0.04 | 127079 |
| 92 | $0.05 | 128396 |
| 93 | $0.04 | 129348 |
| 94 | $0.16 | 145152 |
| 95 | $0.05 | 145529 |
| 96 | $0.04 | 145965 |
| 97 | $0.04 | 146484 |
| 98 | $0.04 | 146853 |
| 99 | $0.05 | 147357 |
| 100 | $0.06 | 150702 |
| 101 | $0.05 | 151613 |
| 102 | $0.04 | 151969 |
| 103 | $0.05 | 152408 |
| 104 | $0.04 | 152781 |
| 105 | $0.05 | 153612 |
| 106 | $0.04 | 154354 |
| 107 | $0.05 | 155065 |
| 108 | $0.04 | 155549 |
| 109 | $0.05 | 155976 |
| 110 | $0.04 | 156622 |
| 111 | $0.05 | 157666 |
| 112 | $0.06 | 159001 |
| 113 | $0.04 | 159925 |
| 114 | $0.05 | 160764 |
| 115 | $0.05 | 161189 |
| 116 | $0.04 | 161618 |
| 117 | $0.05 | 161916 |
| 118 | $0.05 | 162521 |
| 119 | $0.05 | 164262 |
| 120 | $0.05 | 165088 |
| 121 | $0.05 | 165641 |
| 122 | $0.04 | 165872 |
| 123 | $0.51 | 80228 |
| 124 | $0.08 | 86679 |
| 125 | $0.04 | 88468 |
| 126 | $0.03 | 89855 |
| 127 | $0.05 | 91926 |
| 128 | $0.03 | 92450 |
| 129 | $0.03 | 92926 |
| 130 | $0.03 | 93536 |
| 131 | $0.03 | 93847 |
| 132 | $0.03 | 94234 |
| 133 | $0.03 | 94762 |
| 134 | $0.03 | 95056 |
| 135 | $0.03 | 95390 |
| 136 | $0.03 | 95812 |
| 137 | $0.04 | 96681 |
| 138 | $0.06 | 101284 |
| 139 | $0.05 | 102993 |
| 140 | $0.03 | 103820 |
| 141 | $0.04 | 105130 |
| 142 | $0.04 | 105692 |
| 143 | $0.03 | 106130 |
| 144 | $0.03 | 106616 |
| 145 | $0.04 | 107167 |
| 146 | $0.10 | 116391 |
| 147 | $0.04 | 116772 |
| 148 | $0.04 | 117478 |
| 149 | $0.03 | 117847 |
| 150 | $0.04 | 118105 |
| 151 | $0.03 | 118328 |
| 152 | $0.04 | 119432 |
| 153 | $0.04 | 120078 |
| 154 | $0.04 | 121022 |
| 155 | $0.04 | 121565 |
| 156 | $0.04 | 122470 |
| 157 | $0.04 | 124126 |
| 158 | $0.04 | 124947 |
| 159 | $0.05 | 126742 |
| 160 | $0.04 | 127479 |
| 161 | $0.04 | 128295 |
| 162 | $0.04 | 129206 |
| 163 | $0.11 | 138322 |
| 164 | $0.04 | 138883 |
| 165 | $0.04 | 139741 |
| 166 | $0.06 | 141961 |
| 167 | $0.08 | 147140 |
| 168 | $0.04 | 148308 |
| 169 | $0.05 | 149380 |
| 170 | $0.50 | 80226 |
| 171 | $0.07 | 86992 |
| 172 | $0.03 | 88697 |
| 173 | $0.03 | 90487 |
| 174 | $0.03 | 91870 |
| 175 | $0.02 | 92336 |
| 176 | $0.02 | 92770 |
| 177 | $0.02 | 93183 |
| 178 | $0.02 | 93630 |
| 179 | $0.03 | 94461 |
| 180 | $0.06 | 99057 |
| 181 | $0.03 | 100496 |
| 182 | $0.02 | 101091 |
| 183 | $0.02 | 101593 |
| 184 | $0.02 | 101978 |
| 185 | $0.02 | 102451 |
| 186 | $0.03 | 103685 |
| 187 | $0.03 | 104478 |
| 188 | $0.03 | 105141 |
| 189 | $0.02 | 105537 |
| 190 | $0.03 | 106276 |
| 191 | $0.03 | 106845 |
| 192 | $0.03 | 107552 |
| 193 | $0.03 | 108155 |
| 194 | $0.03 | 108901 |
| 195 | $0.02 | 109280 |
| 196 | $0.03 | 109781 |
| 197 | $0.03 | 110285 |
| 198 | $0.03 | 111005 |
| 199 | $0.03 | 111386 |
| 200 | $0.03 | 112136 |
| 201 | $0.03 | 112684 |
| 202 | $0.02 | 112931 |
| 203 | $0.03 | 113422 |
| 204 | $0.03 | 114410 |
| 205 | $0.15 | 130906 |
| 206 | $0.03 | 131286 |
| 207 | $0.03 | 131567 |
| 208 | $0.03 | 132111 |
| 209 | $0.03 | 132538 |
| 210 | $0.03 | 133030 |

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
| plan | 4 | 4 | 0 | 0 | 41 | 31 | 5 | 10 | 3474 | 30810 | 72614 | 0.22 |
| red | 16 | 6 | 1 | 0 | 463 | 328 | 82 | 160 | 33172 | 1599878 | 342771 | 1.50 |
| green | 15 | 5 | 2 | 0 | 732 | 236 | 82 | 144 | 21024 | 1275157 | 224305 | 1.03 |
| refactor | 5 | 0 | 0 | 0 | 44 | 31 | 14 | 28 | 1778 | 202773 | 71914 | 0.22 |
| pin | 1 | 1 | 0 | 0 | 15 | 8 | 2 | 4 | 768 | 23514 | 14385 | 0.05 |
| predicate | 4 | 0 | 0 | 0 | 38 | 26 | 11 | 22 | 1836 | 144359 | 48573 | 0.15 |
| cover | 2 | 0 | 0 | 0 | 40 | 28 | 13 | 22 | 2504 | 178075 | 28420 | 0.11 |
| structural | 2 | 0 | 0 | 0 | 40 | 30 | 10 | 20 | 3224 | 163559 | 29951 | 0.12 |
| transform | 2 | 2 | 0 | 0 | 30 | 22 | 8 | 16 | 1540 | 115729 | 26101 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 21 | 18 | 3 | 0 | 747 | 250 | 73 | 146 | 21427 | 1127409 | 306243 | 1.09 |
| developer | claude-sonnet-5-5 | 24 | 0 | 0 | 0 | 481 | 330 | 122 | 220 | 31926 | 2032790 | 416133 | 1.56 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 215 | 160 | 32 | 60 | 15967 | 573655 | 136658 | 0.84 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 179 | 0.63 |
| green | 658 | 0.67 | 46 | 0.10 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |
| revise-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `release-issue.sh` on an issue labelled only `taken:<lane>` whose comment starts `### ⛔ Preflight refused`, driven through the real REST adapter of `github.py` with only the gh process boundary faked by a fixture (the issue's labels, and its comments at `issues/<n>/comments`), exits 0 and swaps `taken:<lane>` for the opt-in label (fails on current code with exit 3; a small case, no real process) ⟦criterion 3⟧ | 9 | 2 | 2 | 0 | 0 | 0 | 152 | 42 | 84 | 14142 | 793644 | 135762 | 0.69 | 638 | 2/2 | 0/5 | nothing-left |  |  | full |
| The REST adapter's `issue_view(n, "comments")` returns the comment bodies of every page of `issues/<n>/comments`: a fixture of two pages with the `### ⛔ Preflight refused` comment on page 2 has that comment's body in the answer ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 9 | 18 | 3339 | 180061 | 36161 | 0.14 | unknown | unknown | unknown | unknown |  |  | pin |
| The graphql adapter's `issue_view(n, "comments")` returns the issue's comment bodies of every page, not its label names: two pages, the `### ⛔ Preflight refused` comment on page 2, in the answer ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 67 | 22 | 40 | 5707 | 342647 | 88232 | 0.31 | 597 | unknown | 0/5 | nothing-left |  |  | full |
| The REST adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the issue body ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 55 | 19 | 36 | 5035 | 288747 | 78589 | 0.28 | 312 | unknown | 0/5 | nothing-left |  |  | full |
| The graphql adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the label names ⟦criterion 2⟧ | 15 | 4 | 0 | 0 | 0 | 0 | 168 | 61 | 118 | 13939 | 932781 | 215049 | 0.77 | 254 | unknown | 0/5 | nothing-left |  |  | full |
| A failing comments page (a non-zero gh rc in `skills/tdd/scripts/veri/github.py`'s `_comments`) raises `NoAnswer`, so `release-issue.sh` exits 2, not 1; a small unit case driven in-process with `run_cli`, faking only the gh process boundary ⟦added⟧ ⟦criterion 2⟧ | 6 | 1 | 1 | 0 | 0 | 0 | 162 | 40 | 66 | 17187 | 654130 | 137982 | 0.73 | unknown | 1/2 | unknown | unknown |  |  | full |
| `gh_issue_view(n, "comments")` in `skills/tdd/scripts/veri/github.py` raises `NoAnswer`, not `JSONDecodeError`, when a comments page fails (a non-zero gh rc in `_comments`); `release-issue.sh` then exits 3 with `comments unreadable`, as the frozen #3627 case expects; a small unit case faking only the gh process boundary ⟦added⟧ ⟦criterion 2⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 74 | 29 | 54 | 6497 | 511034 | 94645 | 0.35 | 264 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `release-issue.sh` on an issue labelled only `taken:<lane>` whose comment starts `### ⛔ Preflight refused`, driven through the real REST adapter of `github.py` with only the gh process boundary faked by a fixture (the issue's labels, and its comments at `issues/<n>/comments`), exits 0 and swaps `taken:<lane>` for the opt-in label (fails on current code with exit 3; a small case, no real process) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.05 |
| The graphql adapter's `issue_view(n, "comments")` returns the issue's comment bodies of every page, not its label names: two pages, the `### ⛔ Preflight refused` comment on page 2, in the answer ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.04 |
| The REST adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the issue body ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| The graphql adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the label names ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| `gh_issue_view(n, "comments")` in `skills/tdd/scripts/veri/github.py` raises `NoAnswer`, not `JSONDecodeError`, when a comments page fails (a non-zero gh rc in `_comments`); `release-issue.sh` then exits 3 with `comments unreadable`, as the frozen #3627 case expects; a small unit case faking only the gh process boundary ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 11 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| `release-issue.sh` on an issue labelled only `taken:<lane>` whose comment starts `### ⛔ Preflight refused`, driven through the real REST adapter of `github.py` with only the gh process boundary faked by a fixture (the issue's labels, and its comments at `issues/<n>/comments`), exits 0 and swaps `taken:<lane>` for the opt-in label (fails on current code with exit 3; a small case, no real process) ⟦criterion 3⟧ | 1 | 0 | 1 | nothing-left 1 |
| The graphql adapter's `issue_view(n, "comments")` returns the issue's comment bodies of every page, not its label names: two pages, the `### ⛔ Preflight refused` comment on page 2, in the answer ⟦criterion 1⟧ | 1 | 0 | 1 | nothing-left 1 |
| The REST adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the issue body ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| The graphql adapter's `issue_view` with a field it does not know raises `NoAnswer` rather than returning the label names ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| `gh_issue_view(n, "comments")` in `skills/tdd/scripts/veri/github.py` raises `NoAnswer`, not `JSONDecodeError`, when a comments page fails (a non-zero gh rc in `_comments`); `release-issue.sh` then exits 3 with `comments unreadable`, as the frozen #3627 case expects; a small unit case faking only the gh process boundary ⟦added⟧ ⟦criterion 2⟧ | 1 | 0 | 1 | nothing-left 1 |
| issue | 6 | ? | ? | nothing-left 5, nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 2 | 2 | 4 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 2 | 2 | 3 | 4 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 8 | 9 | 7 | 6 | 7 | 6 | 7 | 6 | 10 | 23 | 8 | 11 | 7 | 7 | 6 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 2 | 3 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 1 | 2 | 2 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 227 | 426 | 69320 | 3733854 | 859034 | 14.07 (estimate) |
