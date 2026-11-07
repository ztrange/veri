### 📊 Metrics — issue 3155

Wall time for the issue: 3341 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/3197.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 16 | 14 | 3 | 6 | 1461 | 38217 | 21360 | 0.07 |
| red | 8 | 4 | 0 | 0 | 246 | 130 | 34 | 68 | 11557 | 530705 | 124768 | 0.48 |
| green | 12 | 3 | 3 | 0 | 713 | 223 | 59 | 114 | 19529 | 949633 | 135605 | 0.72 |
| refactor | 3 | 0 | 0 | 0 | 32 | 25 | 8 | 12 | 1093 | 69509 | 37859 | 0.11 |
| red-missing | 2 | 0 | 0 | 0 | 38 | 29 | 11 | 18 | 3476 | 148427 | 30887 | 0.13 |
| pin | 2 | 2 | 0 | 0 | 45 | 33 | 11 | 20 | 3345 | 152956 | 28872 | 0.12 |
| prose | 8 | 0 | 0 | 0 | 605 | 588 | 8 | 16 | 92890 | 188730 | 532784 | 2.28 |
| skill-edit | 2 | 0 | 0 | 0 | 36 | 32 | 12 | 18 | 2553 | 649484 | 182519 | 0.55 |
| predicate | 1 | 0 | 0 | 0 | 26 | 24 | 3 | 6 | 534 | 31214 | 16114 | 0.05 |
| cover | 1 | 0 | 0 | 0 | 18 | 11 | 4 | 8 | 1255 | 54870 | 12068 | 0.05 |
| structural | 1 | 0 | 0 | 0 | 11 | 7 | 4 | 8 | 1038 | 54142 | 11219 | 0.04 |
| transform | 1 | 1 | 0 | 0 | 11 | 8 | 4 | 8 | 793 | 46473 | 16486 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 14 | 11 | 3 | 0 | 646 | 220 | 58 | 112 | 20107 | 838732 | 173341 | 0.72 |
| developer | claude-sonnet-5-5 | 18 | 0 | 0 | 0 | 510 | 284 | 83 | 156 | 23974 | 1237414 | 261897 | 1.11 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 1836 | 1.77 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-missing | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| prose | 0 | 0.00 | 0 | 0.00 |
| skill-edit | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `script-help.sh`, a new `/bin/sh` shim over `veri/script_help.py`, called with no argument exits 2 printing the usage line `usage: script-help.sh <name>` on stderr; its case asserts that line by name, so the repo-wide unreachable audit (`test_main_lists_no_unreachable_script_in_this_repository`) lists the script as `test-only:` and stays green until SCRIPTS.md and SKILL.md name it in later steps; unit-tier, run in-process with `run_cli` in skills/tdd/scripts/tests/py/unit/test_script_help.py ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 74 | 26 | 50 | 6287 | 398067 | 77601 | 0.30 | 264 | unknown | 0/5 | nothing-left |  |  | full |
| `script-help.sh <name>` exits 3 and prints nothing on stdout for a name with no entry in the skill's `SCRIPTS.md` (the catalogue beside the `scripts/` directory, e.g. `no-such-script.sh`); the minimum: read the catalogue and answer 3, with no entry matching or printing yet; unit-tier, run in-process with `run_cli` in skills/tdd/scripts/tests/py/unit/test_script_help.py ⟦criterion 1⟧ | 20 | 6 | 3 | 0 | 0 | 0 | 320 | 88 | 164 | 29028 | 1313495 | 250569 | 1.14 | 1117 | 1/2 | 0/5 | nothing-left |  |  | already-satisfied |
| `script-help.sh <name>` prints exactly the one `SCRIPTS.md` entry for that script and exits 0: the column-0 bullet ``- `$S/<name> …`` naming exactly that script (so `pin-recheck.sh` never matches another script's bullet) and its indented continuation lines, up to the next column-0 line, and nothing of any other entry; unit-tier, run in-process with `run_cli` in skills/tdd/scripts/tests/py/unit/test_script_help.py ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 9 | 18 | 3685 | 139668 | 29821 | 0.13 | 107 | unknown | unknown | unknown |  |  | pin |
| skills/tdd/SCRIPTS.md catalogues `script-help.sh <name>` (prints the one catalogue entry for that script; exits 0 printed / 3 no entry / 2 no argument) under an SC row of its own ⟦skill-edit⟧ | 4 | 0 | 0 | 0 | 0 | 0 | 128 | 9 | 16 | 19039 | 327247 | 177306 | 0.67 | unknown | unknown | unknown | unknown |  |  | full |
| skills/tdd/SKILL.md: the scripts section's pointer to the catalogue (`<base directory>/SCRIPTS.md`) names `$S/script-help.sh <name>` as the way to read one script's entry, rather than reading or grepping the whole file (SS3) ⟦skill-edit⟧ ⟦criterion 2⟧ | 8 | 1 | 0 | 0 | 0 | 0 | 397 | 24 | 44 | 56889 | 694634 | 416485 | 1.68 | 375 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `script-help.sh`, a new `/bin/sh` shim over `veri/script_help.py`, called with no argument exits 2 printing the usage line `usage: script-help.sh <name>` on stderr; its case asserts that line by name, so the repo-wide unreachable audit (`test_main_lists_no_unreachable_script_in_this_repository`) lists the script as `test-only:` and stays green until SCRIPTS.md and SKILL.md name it in later steps; unit-tier, run in-process with `run_cli` in skills/tdd/scripts/tests/py/unit/test_script_help.py ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 5 | 0.03 |
| `script-help.sh <name>` exits 3 and prints nothing on stdout for a name with no entry in the skill's `SCRIPTS.md` (the catalogue beside the `scripts/` directory, e.g. `no-such-script.sh`); the minimum: read the catalogue and answer 3, with no entry matching or printing yet; unit-tier, run in-process with `run_cli` in skills/tdd/scripts/tests/py/unit/test_script_help.py ⟦criterion 1⟧ | 2 | 0/5 | nothing-left | skipped | 0 | 27 | 0.08 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 2 | 4 | 2 | 1 | 0 | 1 | 2 | 2 | 0 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 1 | 1 | 0 |
| fast | 18 | 19 | 24 | 19 | 19 | 20 | 20 | 19 | 20 | 19 | 19 | 19 | 19 | 19 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 161 | 302 | 139524 | 2914360 | 1150541 | 4.66 |
