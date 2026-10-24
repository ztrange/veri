### 📊 Metrics — issue 2034

Wall time for the issue: 2767 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 8 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2306.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.65 over 78 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90260 |
| 2 | $0.02 | 90759 |
| 3 | $0.03 | 92710 |
| 4 | $0.03 | 94647 |
| 5 | $0.02 | 94999 |
| 6 | $0.02 | 95412 |
| 7 | $0.02 | 95741 |
| 8 | $0.02 | 96062 |
| 9 | $0.03 | 96786 |
| 10 | $0.02 | 97114 |
| 11 | $0.06 | 101778 |
| 12 | $0.04 | 104808 |
| 13 | $0.05 | 108109 |
| 14 | $0.04 | 110838 |
| 15 | $0.05 | 113739 |
| 16 | $0.03 | 115120 |
| 17 | $0.06 | 119839 |
| 18 | $0.05 | 122520 |
| 19 | $0.03 | 123764 |
| 20 | $0.04 | 125594 |
| 21 | $0.05 | 128281 |
| 22 | $0.04 | 129507 |
| 23 | $0.04 | 131740 |
| 24 | $0.04 | 133423 |
| 25 | $0.03 | 134084 |
| 26 | $0.03 | 134605 |
| 27 | $0.03 | 135136 |
| 28 | $0.03 | 135381 |
| 29 | $0.03 | 136294 |
| 30 | $0.07 | 142046 |
| 31 | $0.03 | 142810 |
| 32 | $0.04 | 144111 |
| 33 | $0.03 | 144510 |
| 34 | $0.03 | 145040 |
| 35 | $0.03 | 145719 |
| 36 | $0.05 | 148033 |
| 37 | $0.03 | 148406 |
| 38 | $0.04 | 149360 |
| 39 | $0.03 | 149846 |
| 40 | $0.04 | 150908 |
| 41 | $0.03 | 151276 |
| 42 | $0.04 | 152581 |
| 43 | $0.05 | 155015 |
| 44 | $0.04 | 155907 |
| 45 | $0.04 | 157260 |
| 46 | $0.04 | 158887 |
| 47 | $0.04 | 160097 |
| 48 | $0.04 | 160616 |
| 49 | $0.03 | 160908 |
| 50 | $0.04 | 161620 |
| 51 | $0.05 | 163550 |
| 52 | $0.04 | 164492 |
| 53 | $0.04 | 165444 |
| 54 | $0.05 | 167480 |
| 55 | $0.05 | 169439 |
| 56 | $0.04 | 170471 |
| 57 | $0.04 | 170785 |
| 58 | $0.04 | 171080 |
| 59 | $0.04 | 171931 |
| 60 | $0.04 | 172490 |
| 61 | $0.05 | 174002 |
| 62 | $0.04 | 174840 |
| 63 | $0.04 | 175993 |
| 64 | $0.04 | 176356 |
| 65 | $0.04 | 176851 |
| 66 | $0.05 | 178147 |
| 67 | $0.04 | 179249 |
| 68 | $0.04 | 179959 |
| 69 | $0.04 | 180721 |
| 70 | $0.06 | 183618 |
| 71 | $0.05 | 184763 |
| 72 | $0.05 | 185914 |
| 73 | $0.04 | 186663 |
| 74 | $0.04 | 187464 |
| 75 | $0.04 | 188340 |
| 76 | $0.04 | 188814 |
| 77 | $0.04 | 189152 |
| 78 | $0.04 | 189720 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 18 | 15 | 1 | 2 | 2098 | 17442 | 15709 | 0.06 |
| diff | 8 | 4 | 0 | 0 | 736 | 162 | 56 | 112 | 17050 | 1861882 | 178208 | 0.80 |
| red | 4 | 1 | 0 | 0 | 101 | 79 | 25 | 50 | 10035 | 835439 | 83184 | 0.39 |
| pin | 2 | 2 | 0 | 0 | 31 | 20 | 8 | 16 | 2213 | 221291 | 30383 | 0.12 |
| green | 2 | 1 | 0 | 0 | 72 | 28 | 12 | 24 | 3097 | 367617 | 34253 | 0.15 |
| refactor | 1 | 0 | 0 | 0 | 5 | 3 | 2 | 4 | 179 | 49434 | 14871 | 0.04 |
| prose | 3 | 0 | 0 | 0 | 196 | 190 | 3 | 6 | 31859 | 3415 | 297082 | 1.06 |
| skill-edit | 1 | 0 | 0 | 0 | 21 | 19 | 6 | 8 | 1898 | 373776 | 103254 | 0.31 |
| rebase | 4 | 1 | 1 | 0 | 686 | 132 | 42 | 80 | 11743 | 1345183 | 108464 | 0.77 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 10 | 1 | 0 | 682 | 163 | 53 | 104 | 17227 | 1528324 | 194018 | 0.81 |
| developer | claude-sonnet-5-5 | 9 | 0 | 0 | 0 | 539 | 179 | 64 | 128 | 21397 | 2195151 | 201438 | 0.94 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 428 | 97 | 29 | 56 | 7791 | 974813 | 69616 | 0.59 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| rebase | 686 | 0.77 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| docs/adr/0030-tests-change-by-parallel-change-and-mutation-parity.md gains a dated amendment section (2026-10-21, after the original Decision, which stays readable and unedited) stating the phase order expand → cover-new → migrate → contract (a) → contract (b): cover-new adds cases that call the new interface directly with production frozen, and contract (a) deletes the old interface's cases, each deletion proved by mutation parity against a kept case, or moves it to the human as today; docs only, no production or test change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 12 | 24 | 3729 | 350703 | 57500 | 0.22 | 329 | n/a | n/a | n/a |  |  | full |
| The same ADR 0030 amendment section records that the no-product-caller static check gates contract (b) only and that contract (a) starts on migrate's PASS, citing #1475 (folded in from #1526, 2026-10-21); docs only ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 24 | 9 | 18 | 2049 | 249920 | 27682 | 0.11 | 183 | n/a | n/a | n/a |  |  | full |
| `cover-new` joins the interface phases build-develop-prompt.sh and build-verify-prompt.sh accept, placed between expand and migrate (expand, cover-new, migrate, contract-a, contract-b), with new templates skills/tdd/scripts/prompts/develop-cover-new.md (the leaf adds cases that call the new interface directly, runs the affected suites, commits as `test: …`, never modifies a production file: a cover-new commit that touches one is rejected) and verify-cover-new.md (built on _verify-interface-phase-lead.md); every older case that pins the phase lists verbatim (the usage and want strings in skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py and test_build_verify_prompt.py) is updated in the same commit, and tick-ledger.sh --phase-owed still accepts only contract-a and contract-b ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 64 | 21 | 42 | 7420 | 841629 | 57772 | 0.30 | 229 | n/a | n/a | n/a |  |  | full |
| The verify-cover-new prompt's checks REJECT a range that changes a production file, and require that each new case passes against the phase's base sha (the expand commit) and goes red under a mutation of the new interface's behaviour that the verifier applies, runs and restores itself, before it may PASS; the rendered prompt text and any pin it moves land in one commit ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 39 | 14 | 28 | 3852 | 419630 | 35254 | 0.17 | 100 | n/a | n/a | n/a |  |  | full |
| `build-develop-prompt.sh revise … cover-new` freezes production, as a revise of contract-a does (it tells the leaf production files are frozen, not test files), while expand, migrate and contract-b revises still freeze tests (small in-process case in skills/tdd/scripts/tests/py/unit/test_build_develop_prompt.py) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 9 | 18 | 3261 | 279997 | 35903 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `ledger-steps.sh next-phase` never hands over migrate while the step lists cover-new and cover-new is not marked done, whatever order the step lists them in (a step `⟦phases: expand, migrate, cover-new⟧` marked `⟂ expand done` gets cover-new), and `tick-ledger.sh --phase migrate` on such a step exits 2 leaving the ledger byte-identical (small in-process cases in skills/tdd/scripts/tests/py/unit/test_ledger_steps.py and test_tick_ledger.py) ⟦criterion 4⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 67 | 24 | 48 | 7947 | 741768 | 89396 | 0.38 | 213 | unknown | 0/5 | nothing-left |  |  | full |
| A resumed run starts at the first unmarked phase, cover-new included: for a step `⟦phases: expand, cover-new, migrate, contract-a, contract-b⟧` marked `⟂ expand done`, `ledger-steps.sh next-phase` prints cover-new, and once `⟂ cover-new done` is added it prints migrate (small in-process case in skills/tdd/scripts/tests/py/unit/test_ledger_steps.py) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 14 | 28 | 4316 | 452016 | 37392 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| skills/tdd/SKILL.md ⟦skill-edit⟧ ⟦criterion 6⟧ | 7 | 1 | 1 | 0 | 0 | 0 | 273 | 50 | 92 | 33716 | 1720991 | 409983 | 1.78 | 173 | 1/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `ledger-steps.sh next-phase` never hands over migrate while the step lists cover-new and cover-new is not marked done, whatever order the step lists them in (a step `⟦phases: expand, migrate, cover-new⟧` marked `⟂ expand done` gets cover-new), and `tick-ledger.sh --phase migrate` on such a step exits 2 leaving the ledger byte-identical (small in-process cases in skills/tdd/scripts/tests/py/unit/test_ledger_steps.py and test_tick_ledger.py) ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.04 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 15 | 16 | 16 |  |  |  |
| affected | 105 | 101 | 2 | 63 | 4 | 2 | 4 | 2 | 1 | 1 | 1 | 2 | 1 | 113 |
| target | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |
| all | 107 | 108 | 109 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 155 | 302 | 80172 | 5075479 | 865408 | 3.72 |
