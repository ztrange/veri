### 📊 Metrics — issue 2687

Wall time for the issue: 12140 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2722.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.67 over 72 turns, in 3 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 86100 tokens, largest 119329 tokens
Conductor context: first turn 86091 tokens, largest 118231 tokens
Conductor context: first turn 86094 tokens, largest 152933 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 86100 |
| 2 | $0.08 | 93102 |
| 3 | $0.10 | 101512 |
| 4 | $0.05 | 103899 |
| 5 | $0.04 | 104552 |
| 6 | $0.05 | 106411 |
| 7 | $0.06 | 109993 |
| 8 | $0.04 | 111561 |
| 9 | $0.05 | 112457 |
| 10 | $0.06 | 116341 |
| 11 | $0.05 | 117907 |
| 12 | $0.05 | 119329 |
| 13 | $0.56 | 86091 |
| 14 | $0.09 | 93093 |
| 15 | $0.10 | 101503 |
| 16 | $0.06 | 103858 |
| 17 | $0.04 | 104895 |
| 18 | $0.05 | 106864 |
| 19 | $0.05 | 108126 |
| 20 | $0.08 | 113841 |
| 21 | $0.06 | 117236 |
| 22 | $0.05 | 118231 |
| 23 | $0.55 | 86094 |
| 24 | $0.07 | 93097 |
| 25 | $0.09 | 102100 |
| 26 | $0.04 | 104405 |
| 27 | $0.03 | 104977 |
| 28 | $0.04 | 107494 |
| 29 | $0.03 | 108539 |
| 30 | $0.03 | 109370 |
| 31 | $0.03 | 110924 |
| 32 | $0.11 | 122236 |
| 33 | $0.06 | 126506 |
| 34 | $0.04 | 128266 |
| 35 | $0.05 | 131335 |
| 36 | $0.04 | 132928 |
| 37 | $0.03 | 133317 |
| 38 | $0.04 | 134522 |
| 39 | $0.04 | 135828 |
| 40 | $0.04 | 137500 |
| 41 | $0.03 | 137987 |
| 42 | $0.03 | 138666 |
| 43 | $0.03 | 139508 |
| 44 | $0.03 | 139741 |
| 45 | $0.03 | 139982 |
| 46 | $0.03 | 140356 |
| 47 | $0.04 | 142432 |
| 48 | $0.03 | 142886 |
| 49 | $0.03 | 143206 |
| 50 | $0.03 | 143791 |
| 51 | $0.03 | 144238 |
| 52 | $0.03 | 144474 |
| 53 | $0.03 | 144792 |
| 54 | $0.03 | 145368 |
| 55 | $0.03 | 145914 |
| 56 | $0.03 | 146138 |
| 57 | $0.03 | 146444 |
| 58 | $0.04 | 147514 |
| 59 | $0.03 | 147921 |
| 60 | $0.03 | 148159 |
| 61 | $0.03 | 148456 |
| 62 | $0.04 | 149278 |
| 63 | $0.03 | 149621 |
| 64 | $0.03 | 150010 |
| 65 | $0.04 | 151008 |
| 66 | $0.04 | 151629 |
| 67 | $0.03 | 151899 |
| 68 | $0.04 | 152590 |
| 69 | $0.03 | 152933 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 11 | 1 | 2 | 1339 | 0 | 40089 | 0.11 |
| prose | 8 | 0 | 0 | 0 | 96 | 72 | 8 | 16 | 10396 | 11464 | 81001 | 0.31 |
| diff | 10 | 5 | 0 | 0 | 8860 | 173 | 38 | 76 | 11463 | 624727 | 839296 | 2.28 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 4737 | 87 | 17 | 34 | 6242 | 216740 | 423399 | 1.14 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 4136 | 97 | 22 | 44 | 6560 | 407987 | 455986 | 1.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 52 | 0.16 |
| diff | 0 | 0.00 | 8860 | 2.28 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Add AG1–AG7 to `docs/adr/REQUIREMENTS.md` under `## docs/adr/0016-uncovered-lines-are-debt-the-page-reports.md`, exactly as they appear in the issue, grade the unit PASS against its whole list with no edit to the ADR, and sign it in `docs/adr/GRADED`, so `GRADED` carries a line for the unit whose signature matches its current text and `prose-owed.sh` does not name it: unit docs/adr/0016-uncovered-lines-are-debt-the-page-reports.md ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 11 | 1 | 2 | 1654 | 649 | 10671 | 0.04 | unknown | unknown | unknown | unknown |  |  | full |
| Add AP1–AP7 to `docs/adr/REQUIREMENTS.md` under `## docs/adr/0018-a-preamble-token-is-priced-per-night.md`, exactly as they appear in the issue, grade the unit PASS against its whole list with no edit to the ADR, and sign it in `docs/adr/GRADED`, so `GRADED` carries a line for the unit whose signature matches its current text and `prose-owed.sh` does not name it: unit docs/adr/0018-a-preamble-token-is-priced-per-night.md ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 7 | 1 | 2 | 1082 | 1545 | 10070 | 0.04 | unknown | unknown | unknown | unknown |  |  | full |
| Add AC1–AC8 to `docs/adr/REQUIREMENTS.md` under `## docs/adr/0019-the-contingent-half-of-skill-md-stays-resident.md`, exactly as they appear in the issue, grade the unit PASS against its whole list with no edit to the ADR, and sign it in `docs/adr/GRADED`, so `GRADED` carries a line for the unit whose signature matches its current text and `prose-owed.sh` does not name it: unit docs/adr/0019-the-contingent-half-of-skill-md-stays-resident.md ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 8 | 1 | 2 | 1112 | 1545 | 10119 | 0.04 | unknown | unknown | unknown | unknown |  |  | full |
| Add AN1–AN10 to `docs/adr/REQUIREMENTS.md` under `## docs/adr/0020-a-clean-exit-with-no-verdict-is-relaunched.md`, exactly as they appear in the issue, grade the unit PASS against its whole list with no edit to the ADR, and sign it in `docs/adr/GRADED`, so `GRADED` carries a line for the unit whose signature matches its current text and `prose-owed.sh` prints nothing: unit docs/adr/0020-a-clean-exit-with-no-verdict-is-relaunched.md ⟦skill-edit⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 15 | 1 | 2 | 1593 | 1545 | 10164 | 0.04 | unknown | unknown | unknown | unknown |  |  | full |
| Delete `docs/tests/docs-gap-adr.test.sh` whole; in `docs/tests/suite-lanes.test.sh` delete `ADR_SUITE`, `ADR_SUITE_PATH`, `probe_adr_in_docs_roster`, `probe_adr_runs_there`, `probe_rehomed_header` and the header comment's account of the ADR suite (lines 9-17), and rename case 1 to "no suite 'make test' runs is about the docs pipeline", keeping `probe_dev_lane_clean`; reword the sentence of `docs/merge-gates.sh`'s header (lines 44-45) so it names no deleted suite and still carries the two facts `probe_widened_selection` and `probe_no_stale_trigger` read from that header; `make docs-test` stays green, no ADR edited ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 1 | 0 | 53 | 11 | 20 | 4504 | 214656 | 229941 | 0.64 | unknown | n/a | n/a | n/a |  |  | full |
| Delete `docs/tests/preamble-cost-adr.test.sh` whole, its two cases with it; `make docs-test` stays green, no ADR edited ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 14 | 6 | 12 | 1564 | 71677 | 145604 | 0.39 | unknown | n/a | n/a | n/a |  |  | full |
| Delete `docs/tests/no-verdict-relaunch-adr.test.sh` whole, its one case with it; `make docs-test` stays green, no ADR edited ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 6 | 12 | 1526 | 71637 | 146475 | 0.39 | unknown | n/a | n/a | n/a |  |  | full |
| In `docs/tests/suite-lanes.test.sh` delete `probe_suite_home_prose` and its call in case 2, the `GATE_ROW_WHERE` call of `probe_widened_selection` in `probe_gate_rule_prose`, the `GATE_ROW_WHERE` call of `probe_no_stale_trigger` in `probe_stale_trigger_gone`, then `gate_row` and `GATE_ROW_WHERE`, keeping `probe_dev_lane_clean` and the Makefile-comment and `docs/merge-gates.sh`-header calls; `make docs-test` stays green, no ADR edited ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 8 | 18 | 2267 | 157066 | 168316 | 0.46 | unknown | n/a | n/a | n/a |  |  | full |
| With the deletions in place, no suite under `docs/tests/` reads a file under `docs/adr/` (`merge-gates.test.sh` plants its own, which is not a read of a real record) and `make docs-test` passes; this step makes no commit of its own, and the PR body's map of each deleted case or probe to its row (AG, AP, AC, AN, CY75, CM10, CM67), or why it carries none, is written at the Draft PR step ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 7 | 14 | 1602 | 109691 | 148960 | 0.40 | unknown | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| fast | 27 | 30 | 25 | 32 | 32 |
| affected | 594 | 595 | 584 | 801 |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 47 | 94 | 23198 | 636191 | 960386 | 7.36 (estimate) |
