Closes #3708 — a behaviour-preserving refactor of `skills/tdd/scripts/veri/status.py`. The plan had 3 refactoring steps and one full-suite line, each step Cover → Transform → blind transform verify. The ledger is committed at `.tdd/issue-3708.md`.

- **Step 1:** `read_role_state` returns `None` for a missing role-state file, so a missing file is now distinguishable from an empty one. Both `dispatch.py` callers, `recover_items` and `recover_state` treat `None` as no lines.
- **Step 2:** `recover_state` returns `["no state file"]` from that `None` and no longer calls `os.path.exists`. Step 1's transform already did this, so the predicate held without a leaf.
- **Step 3:** both "GitHub refused the … read" `OSError`s in `recover_prs` are raised from one helper, `refused_read_check(answer, what)`, with the message text unchanged. This step resumed after #3720 pinned the single pull request read's refusal, which the first cover found unpinned.
- **Full suite:** `make test` is green on the rebased tip (6514 passed), and CI is green.

### 📊 Metrics — issue 3708

Wall time for the issue: 1728 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3719.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.69 over 97 turns, in 2 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 80336 tokens, largest 141223 tokens
Conductor context: first turn 80491 tokens, largest 154313 tokens
The per-turn dollars are estimated: each turn's non-output usage priced, plus a share of the result record's remaining cost.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.51 | 80336 |
| 2 | $0.08 | 87101 |
| 3 | $0.04 | 88180 |
| 4 | $0.04 | 90093 |
| 5 | $0.04 | 91385 |
| 6 | $0.03 | 91740 |
| 7 | $0.03 | 92199 |
| 8 | $0.03 | 92548 |
| 9 | $0.03 | 92878 |
| 10 | $0.03 | 93177 |
| 11 | $0.03 | 93649 |
| 12 | $0.03 | 94216 |
| 13 | $0.04 | 95015 |
| 14 | $0.05 | 97544 |
| 15 | $0.05 | 100404 |
| 16 | $0.04 | 102070 |
| 17 | $0.04 | 103265 |
| 18 | $0.03 | 103694 |
| 19 | $0.04 | 104878 |
| 20 | $0.04 | 105452 |
| 21 | $0.03 | 106002 |
| 22 | $0.04 | 106791 |
| 23 | $0.05 | 108584 |
| 24 | $0.05 | 110908 |
| 25 | $0.03 | 111389 |
| 26 | $0.04 | 111740 |
| 27 | $0.04 | 112671 |
| 28 | $0.04 | 113792 |
| 29 | $0.03 | 114304 |
| 30 | $0.04 | 115458 |
| 31 | $0.04 | 116427 |
| 32 | $0.11 | 125709 |
| 33 | $0.04 | 126502 |
| 34 | $0.05 | 127982 |
| 35 | $0.04 | 128731 |
| 36 | $0.04 | 129293 |
| 37 | $0.04 | 129803 |
| 38 | $0.04 | 130349 |
| 39 | $0.04 | 130810 |
| 40 | $0.04 | 131684 |
| 41 | $0.04 | 132295 |
| 42 | $0.05 | 133354 |
| 43 | $0.07 | 138606 |
| 44 | $0.04 | 139101 |
| 45 | $0.05 | 139685 |
| 46 | $0.04 | 140281 |
| 47 | $0.04 | 141223 |
| 48 | $0.50 | 80491 |
| 49 | $0.07 | 87356 |
| 50 | $0.03 | 88432 |
| 51 | $0.03 | 90374 |
| 52 | $0.04 | 92652 |
| 53 | $0.02 | 93274 |
| 54 | $0.04 | 96497 |
| 55 | $0.03 | 97315 |
| 56 | $0.02 | 97889 |
| 57 | $0.02 | 98124 |
| 58 | $0.02 | 98432 |
| 59 | $0.02 | 98691 |
| 60 | $0.02 | 99010 |
| 61 | $0.03 | 99763 |
| 62 | $0.02 | 100269 |
| 63 | $0.02 | 100581 |
| 64 | $0.02 | 100837 |
| 65 | $0.07 | 106918 |
| 66 | $0.04 | 108753 |
| 67 | $0.03 | 109433 |
| 68 | $0.03 | 110049 |
| 69 | $0.03 | 110690 |
| 70 | $0.03 | 111830 |
| 71 | $0.03 | 113224 |
| 72 | $0.03 | 113930 |
| 73 | $0.03 | 115082 |
| 74 | $0.05 | 118662 |
| 75 | $0.03 | 119283 |
| 76 | $0.09 | 127288 |
| 77 | $0.03 | 127883 |
| 78 | $0.03 | 128366 |
| 79 | $0.03 | 128727 |
| 80 | $0.03 | 128978 |
| 81 | $0.03 | 129482 |
| 82 | $0.04 | 131210 |
| 83 | $0.03 | 131841 |
| 84 | $0.03 | 132301 |
| 85 | $0.03 | 132954 |
| 86 | $0.03 | 133493 |
| 87 | $0.03 | 133897 |
| 88 | $0.03 | 134832 |
| 89 | $0.16 | 151324 |
| 90 | $0.03 | 151605 |
| 91 | $0.03 | 152012 |
| 92 | $0.04 | 152659 |
| 93 | $0.03 | 152931 |
| 94 | $0.04 | 153645 |
| 95 | $0.03 | 154026 |
| 96 | $0.03 | 154313 |

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
| 🔎 verify-<phase> (revised) | 0 | 0 | $0.00 |
| 🗺️ Plan | 0 | 0 | $0.00 |
| 🗺️ verify-plan | 0 | 0 | $0.00 |
| ▶️ Resuming | 0 | 0 | $0.00 |
| ⛔ Bailed | 0 | 0 | $0.00 |
| ⏹️ Stopped | 0 | 0 | $0.00 |
| Total | 0 | 0 | $0.00 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 2 | 0 | 0 | 29 | 21 | 3 | 6 | 1882 | 20510 | 41658 | 0.13 |
| cover | 3 | 0 | 0 | 0 | 99 | 60 | 20 | 40 | 5462 | 333865 | 57148 | 0.23 |
| transform | 4 | 2 | 0 | 0 | 134 | 61 | 20 | 38 | 5295 | 291628 | 56004 | 0.22 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 84 | 45 | 10 | 20 | 3574 | 116639 | 69310 | 0.22 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 178 | 97 | 33 | 64 | 9065 | 529364 | 85500 | 0.36 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Refactoring "signal a missing file with None": `read_role_state` in `skills/tdd/scripts/veri/status.py` returns `None` (not `[]`) when the role-state file is missing, and every caller handles that case with behaviour unchanged — `dispatch.py`'s two calls (`lines = status.read_role_state("dev", lane())` and `prioritize(free, status.read_role_state("dev", lane()))`) and `status.py`'s `recover_items` and `recover_state`'s field parse treat it as no lines; `recover_state` still returns `["no state file"]` for a missing file. No production behaviour change, no test edited. Predicate (false before, true after): `sed -n '/^def read_role_state/,/^def /p' skills/tdd/scripts/veri/status.py | grep -q 'return None'` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 62 | 19 | 36 | 4685 | 285426 | 49386 | 0.20 | 156 | n/a | n/a | n/a |  |  | full |
| Refactoring "extract the refused-read check": `recover_prs` in `skills/tdd/scripts/veri/status.py` raises both "GitHub refused the ... read" `OSError`s (the open pull request read and the single pull request read for #<n>) from one helper, the message text unchanged for both reads. No production behaviour change, no test edited. Predicate (false before, true after): `[ "$(grep -c 'GitHub refused the' skills/tdd/scripts/veri/status.py)" -eq 1 ]` ⟦criterion 3⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 59 | 21 | 42 | 6072 | 340067 | 63766 | 0.25 | 214 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Refactor totals

| step | passes | transforms | landed nothing | stopped |
| --- | ---: | ---: | ---: | --- |
| issue | 1 | ? | ? | nothing-structural 1 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 0 | 6 | 5 | 5 | 4 | 5 | 5 | 9 | 19 | 19 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 43 | 84 | 12639 | 646003 | 154810 | 5.27 (estimate) |
