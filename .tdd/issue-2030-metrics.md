### 📊 Metrics — issue 2030

Wall time for the issue: 783 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Every figure in this report is wall-clock: the log carries no awake-clock reading, so time the machine spent asleep is counted in them.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2299.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $5.89 over 104 turns, in 2 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.59 | 90109 |
| 2 | $0.04 | 91066 |
| 3 | $0.04 | 92530 |
| 4 | $0.04 | 94512 |
| 5 | $0.04 | 94853 |
| 6 | $0.03 | 95351 |
| 7 | $0.03 | 95702 |
| 8 | $0.03 | 96017 |
| 9 | $0.04 | 96749 |
| 10 | $0.03 | 97096 |
| 11 | $0.05 | 98559 |
| 12 | $0.05 | 101701 |
| 13 | $0.09 | 108271 |
| 14 | $0.05 | 111631 |
| 15 | $0.05 | 112730 |
| 16 | $0.04 | 113738 |
| 17 | $0.05 | 116361 |
| 18 | $0.06 | 118694 |
| 19 | $0.03 | 119164 |
| 20 | $0.05 | 120163 |
| 21 | $0.04 | 120700 |
| 22 | $0.04 | 121412 |
| 23 | $0.14 | 134780 |
| 24 | $0.05 | 135999 |
| 25 | $0.05 | 137979 |
| 26 | $0.05 | 138745 |
| 27 | $0.04 | 139976 |
| 28 | $0.06 | 141759 |
| 29 | $0.04 | 142604 |
| 30 | $0.05 | 142951 |
| 31 | $0.04 | 143862 |
| 32 | $0.05 | 144245 |
| 33 | $0.04 | 145193 |
| 34 | $0.05 | 146305 |
| 35 | $0.08 | 151421 |
| 36 | $0.06 | 153030 |
| 37 | $0.06 | 155381 |
| 38 | $0.05 | 156911 |
| 39 | $0.05 | 157609 |
| 40 | $0.05 | 158708 |
| 41 | $0.05 | 159228 |
| 42 | $0.04 | 159735 |
| 43 | $0.06 | 160799 |
| 44 | $0.04 | 161480 |
| 45 | $0.06 | 162702 |
| 46 | $0.04 | 163018 |
| 47 | $0.07 | 166051 |
| 48 | $0.07 | 168584 |
| 49 | $0.05 | 169341 |
| 50 | $0.05 | 169919 |
| 51 | $0.05 | 170581 |
| 52 | $0.05 | 171506 |
| 53 | $0.05 | 172285 |
| 54 | $0.06 | 174707 |
| 55 | $0.06 | 175343 |
| 56 | $0.04 | 175519 |
| 57 | $0.05 | 175924 |
| 58 | $0.06 | 176772 |
| 59 | $0.05 | 177458 |
| 60 | $0.05 | 178486 |
| 61 | $0.05 | 179116 |
| 62 | $0.05 | 179748 |
| 63 | $0.06 | 180496 |
| 64 | $0.05 | 181167 |
| 65 | $0.05 | 182110 |
| 66 | $0.06 | 182862 |
| 67 | $0.05 | 184003 |
| 68 | $0.06 | 185128 |
| 69 | $0.06 | 186082 |
| 70 | $0.05 | 186969 |
| 71 | $0.08 | 191081 |
| 72 | $0.05 | 191282 |
| 73 | $0.06 | 192588 |
| 74 | $0.06 | 193475 |
| 75 | $0.58 | 90109 |
| 76 | $0.02 | 90522 |
| 77 | $0.03 | 91825 |
| 78 | $0.04 | 94602 |
| 79 | $0.12 | 107676 |
| 80 | $0.03 | 108159 |
| 81 | $0.02 | 108562 |
| 82 | $0.02 | 108876 |
| 83 | $0.02 | 109231 |
| 84 | $0.03 | 109835 |
| 85 | $0.05 | 113042 |
| 86 | $0.03 | 113480 |
| 87 | $0.03 | 114610 |
| 88 | $0.03 | 115044 |
| 89 | $0.03 | 115359 |
| 90 | $0.05 | 118502 |
| 91 | $0.03 | 119126 |
| 92 | $0.03 | 119835 |
| 93 | $0.03 | 120586 |
| 94 | $0.03 | 121218 |
| 95 | $0.03 | 121741 |
| 96 | $0.03 | 122044 |
| 97 | $0.03 | 122741 |
| 98 | $0.03 | 123304 |
| 99 | $0.03 | 123610 |
| 100 | $0.03 | 123871 |
| 101 | $0.03 | 124527 |
| 102 | $0.03 | 124847 |
| 103 | $0.03 | 125121 |
| 104 | $0.03 | 125532 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 14 | 12 | 1 | 2 | 1547 | 17442 | 14575 | 0.05 |
| red | 12 | 4 | 1 | 0 | 239 | 192 | 57 | 108 | 23781 | 1628757 | 242789 | 1.15 |
| green | 6 | 2 | 0 | 0 | 232 | 141 | 38 | 76 | 14123 | 1191872 | 110706 | 0.68 |
| red-supersede | 1 | 0 | 0 | 0 | 43 | 39 | 5 | 10 | 5365 | 162429 | 24057 | 0.13 |
| diff | 4 | 2 | 0 | 0 | 130 | 52 | 20 | 38 | 5858 | 531809 | 82146 | 0.32 |
| refactor | 2 | 0 | 0 | 0 | 14 | 9 | 5 | 10 | 773 | 129490 | 28500 | 0.09 |
| pin | 3 | 3 | 0 | 0 | 53 | 37 | 13 | 26 | 4702 | 358025 | 45519 | 0.20 |
| prose | 3 | 0 | 0 | 0 | 209 | 201 | 3 | 6 | 33141 | 3415 | 296144 | 1.07 |
| skill-edit | 1 | 0 | 0 | 0 | 13 | 10 | 4 | 8 | 1182 | 373958 | 103998 | 0.31 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 13 | 12 | 1 | 0 | 258 | 139 | 45 | 90 | 16382 | 1195920 | 220645 | 0.84 |
| developer | claude-sonnet-5-5 | 13 | 0 | 0 | 0 | 331 | 234 | 70 | 132 | 29491 | 2030429 | 262653 | 1.29 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 136 | 109 | 24 | 48 | 10276 | 793475 | 64994 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 132 | 0.70 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| red-supersede | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| unlabel-issue.sh <n> removes VERI_LABEL from the issue and adds the label `taken:<lane>` to it, `<lane>` being the text after VERI_LABEL's last `:` or `main` when it has none: with VERI_LABEL=ready-for-agent (and unset) the issue gains `taken:main`, with VERI_LABEL=ready-for-agent:mu it gains `taken:mu` (small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py, gh faked at subprocess.run) ⟦criterion 1⟧ | 13 | 4 | 1 | 0 | 0 | 0 | 269 | 64 | 126 | 30515 | 1916082 | 262080 | 1.43 | 270 | red 1/2, green 1/2 | 0/5 | nothing-left |  |  | full |
| The existing cases in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py keep passing when unlabel-issue.sh also creates and adds a `taken:<lane>` label: their fake gh accepts a label-create and an add-label call beside the opt-in label's DELETE without asserting them; no production change, test-only ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 8 | 16 | 3063 | 223135 | 30155 | 0.13 | 87 | n/a | n/a | n/a |  |  | full |
| unlabel-issue.sh creates the `taken:<lane>` label in the repository when it does not exist yet, so the add succeeds and the issue carries it, exit 0 (small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py, gh faked at subprocess.run) ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 11 | 22 | 4351 | 336371 | 35568 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| unlabel-issue.sh exits 0 when the issue already carries `taken:<lane>`, leaving it on the issue (small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py, gh faked at subprocess.run) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 11 | 20 | 4381 | 309046 | 36837 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| unlabel-issue.sh exits 2 with a diagnostic on stderr when gh gives no answer to adding `taken:<lane>` (or to creating the label), as it does for the label removal (small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py, gh faked at subprocess.run) ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 31 | 9 | 16 | 3566 | 234090 | 36330 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| solvable-issues.sh never lists an open, unblocked, unclaimed issue carrying any `taken:*` label (`taken:main`, `taken:mu`), even when it also carries the opt-in label, while an issue carrying only the opt-in label is still listed (in-process case in skills/tdd/scripts/tests/py/test_solvable_issues.py, gh documents faked as that suite already does) ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 52 | 23 | 46 | 5931 | 674984 | 80756 | 0.33 | 177 | unknown | 0/5 | nothing-left |  |  | full |
| skills/tdd/SKILL.md ⟦skill-edit⟧ ⟦criterion 5⟧ | 3 | 0 | 0 | 0 | 0 | 0 | 132 | 6 | 12 | 20859 | 375990 | 301639 | 1.00 | unknown | unknown | unknown | unknown |  |  | full |
| No bail or park path the branch touches removes the `taken:<lane>` label: the branch's diff adds no call removing a `taken:` label from an issue, so a bailed or parked issue keeps it ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 12 | 22 | 2795 | 308674 | 51991 | 0.19 | 89 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| unlabel-issue.sh <n> removes VERI_LABEL from the issue and adds the label `taken:<lane>` to it, `<lane>` being the text after VERI_LABEL's last `:` or `main` when it has none: with VERI_LABEL=ready-for-agent (and unset) the issue gains `taken:main`, with VERI_LABEL=ready-for-agent:mu it gains `taken:mu` (small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py, gh faked at subprocess.run) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.04 |
| solvable-issues.sh never lists an open, unblocked, unclaimed issue carrying any `taken:*` label (`taken:main`, `taken:mu`), even when it also carries the opt-in label, while an issue carrying only the opt-in label is still listed (in-process case in skills/tdd/scripts/tests/py/test_solvable_issues.py, gh documents faked as that suite already does) ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 8 | 0.05 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 |
| fast | 16 | 16 | 16 | 16 | 16 | 15 | 16 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 146 | 284 | 90472 | 4397197 | 948434 | 3.99 |
