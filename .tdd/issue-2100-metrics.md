### 📊 Metrics — issue 2100

Wall time for the issue: 3679 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2126.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $4.37 over 99 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.55 | 86114 |
| 2 | $0.02 | 86595 |
| 3 | $0.02 | 87445 |
| 4 | $0.03 | 89422 |
| 5 | $0.02 | 89683 |
| 6 | $0.02 | 90052 |
| 7 | $0.02 | 90314 |
| 8 | $0.02 | 90650 |
| 9 | $0.02 | 90964 |
| 10 | $0.02 | 91167 |
| 11 | $0.02 | 91510 |
| 12 | $0.02 | 92091 |
| 13 | $0.03 | 92978 |
| 14 | $0.02 | 93573 |
| 15 | $0.04 | 96443 |
| 16 | $0.09 | 104871 |
| 17 | $0.05 | 108511 |
| 18 | $0.02 | 108873 |
| 19 | $0.03 | 109564 |
| 20 | $0.03 | 110079 |
| 21 | $0.03 | 110821 |
| 22 | $0.03 | 111381 |
| 23 | $0.09 | 119342 |
| 24 | $0.03 | 119984 |
| 25 | $0.03 | 120680 |
| 26 | $0.03 | 121372 |
| 27 | $0.03 | 121958 |
| 28 | $0.03 | 122745 |
| 29 | $0.03 | 123965 |
| 30 | $0.03 | 124606 |
| 31 | $0.03 | 125596 |
| 32 | $0.03 | 126417 |
| 33 | $0.08 | 133626 |
| 34 | $0.03 | 134641 |
| 35 | $0.04 | 135956 |
| 36 | $0.04 | 137030 |
| 37 | $0.03 | 137575 |
| 38 | $0.03 | 137984 |
| 39 | $0.03 | 138732 |
| 40 | $0.03 | 138924 |
| 41 | $0.03 | 139698 |
| 42 | $0.03 | 140447 |
| 43 | $0.04 | 141336 |
| 44 | $0.05 | 143558 |
| 45 | $0.04 | 144558 |
| 46 | $0.04 | 145486 |
| 47 | $0.04 | 146619 |
| 48 | $0.04 | 147984 |
| 49 | $0.04 | 149448 |
| 50 | $0.04 | 150191 |
| 51 | $0.04 | 151570 |
| 52 | $0.04 | 152250 |
| 53 | $0.04 | 153190 |
| 54 | $0.04 | 154270 |
| 55 | $0.04 | 155757 |
| 56 | $0.04 | 157360 |
| 57 | $0.04 | 158198 |
| 58 | $0.04 | 159606 |
| 59 | $0.04 | 160337 |
| 60 | $0.04 | 161169 |
| 61 | $0.04 | 162469 |
| 62 | $0.04 | 163874 |
| 63 | $0.04 | 165082 |
| 64 | $0.04 | 165858 |
| 65 | $0.04 | 167310 |
| 66 | $0.04 | 168002 |
| 67 | $0.04 | 169334 |
| 68 | $0.06 | 172013 |
| 69 | $0.05 | 173461 |
| 70 | $0.04 | 174492 |
| 71 | $0.04 | 175204 |
| 72 | $0.05 | 176449 |
| 73 | $0.04 | 177146 |
| 74 | $0.04 | 178003 |
| 75 | $0.05 | 179401 |
| 76 | $0.04 | 180064 |
| 77 | $0.05 | 181378 |
| 78 | $0.04 | 182020 |
| 79 | $0.05 | 183396 |
| 80 | $0.04 | 184079 |
| 81 | $0.04 | 184943 |
| 82 | $0.05 | 186109 |
| 83 | $0.06 | 188528 |
| 84 | $0.04 | 189238 |
| 85 | $0.04 | 189451 |
| 86 | $0.04 | 190332 |
| 87 | $0.04 | 190637 |
| 88 | $0.04 | 190870 |
| 89 | $0.04 | 191288 |
| 90 | $0.05 | 192313 |
| 91 | $0.05 | 193146 |
| 92 | $0.04 | 193483 |
| 93 | $0.04 | 193964 |
| 94 | $0.04 | 194531 |
| 95 | $0.05 | 195616 |
| 96 | $0.04 | 196304 |
| 97 | $0.04 | 196883 |
| 98 | $0.05 | 197836 |
| 99 | $0.04 | 198438 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 1 | 2 | 1352 | 0 | 30390 | 0.09 |
| diff | 2 | 1 | 0 | 0 | 359 | 35 | 10 | 20 | 3420 | 242617 | 62541 | 0.21 |
| red | 12 | 6 | 0 | 0 | 492 | 283 | 59 | 118 | 23922 | 1750745 | 208964 | 0.94 |
| green | 15 | 5 | 2 | 0 | 1013 | 273 | 72 | 132 | 20281 | 1811591 | 217112 | 1.12 |
| refactor | 10 | 5 | 0 | 0 | 319 | 99 | 29 | 56 | 5757 | 695601 | 130686 | 0.45 |
| red-repair | 1 | 0 | 0 | 0 | 41 | 25 | 5 | 10 | 1926 | 143208 | 15638 | 0.07 |
| pin | 1 | 1 | 0 | 0 | 41 | 17 | 4 | 8 | 1394 | 105908 | 15396 | 0.06 |
| cover | 1 | 0 | 0 | 0 | 52 | 22 | 6 | 12 | 1702 | 148882 | 32393 | 0.11 |
| predicate | 2 | 0 | 0 | 0 | 21 | 16 | 5 | 10 | 1430 | 132670 | 13220 | 0.06 |
| structural | 1 | 0 | 0 | 0 | 64 | 11 | 4 | 8 | 1122 | 105672 | 13280 | 0.06 |
| transform | 1 | 1 | 0 | 0 | 37 | 19 | 3 | 6 | 603 | 55170 | 28640 | 0.08 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 22 | 20 | 2 | 0 | 1083 | 336 | 71 | 140 | 23236 | 1752803 | 321670 | 1.21 |
| developer | claude-sonnet-5-5 | 21 | 0 | 0 | 0 | 1135 | 407 | 105 | 202 | 34303 | 2913125 | 354662 | 1.52 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 236 | 68 | 22 | 40 | 5370 | 526136 | 91928 | 0.53 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 529 | 0.69 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| red-repair | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |
| structural | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The existing cases that pin the unset-VERI_PYTEST_WORKERS worker count (test_with_no_worker_count_the_launcher_hands_pytest_one_worker_per_available_core_and_runs_serially_on_a_single_core in skills/tdd/scripts/tests/py/test_pytest_leg.py, and test_with_no_worker_count_set_make_unit_runs_four_workers_and_make_test_one_per_available_core in skills/tdd/scripts/tests/py/test_recipe_one_pytest_process.py) name a private, empty registry of running legs through VERI_PYTEST_LEGS, a directory under their tmp_path, so they go on asserting one worker per core when no other leg runs; test-only, no production change ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 35 | 10 | 20 | 3420 | 242617 | 62541 | 0.21 | 428 | n/a | n/a | n/a |  |  | full |
| With VERI_PYTEST_WORKERS unset, the leg reads the registry of running legs in the directory VERI_PYTEST_LEGS names (one entry per running leg: its pid and its worker count) and takes only the cores the registered legs leave free, at least 1: on a fake 16 cores a leg starting beside one registered 16-worker leg gets 1, and with two legs registered at 8 each a third gets 1; pinned in-process (a small case) with a fake core count and a fake registry under tmp_path ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 145 | 31 | 60 | 10174 | 804721 | 124206 | 0.59 | 594 | 1/2 | 0/5 | nothing-left |  |  | full |
| With VERI_PYTEST_WORKERS and VERI_PYTEST_LEGS both unset, the leg reads and registers in a default registry directory every leg one user starts on the machine shares (under tempfile.gettempdir(), its name carrying the user id), exactly as it does in a named one, so legs nobody configured still share the cores: on a fake 16 cores with one live 16-worker entry in that default directory a leg gets 1; pinned in-process (a small case) with tempfile.gettempdir faked to a directory under tmp_path ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 87 | 27 | 50 | 8481 | 707939 | 91213 | 0.38 | 343 | unknown | 0/5 | nothing-left |  |  | full |
| With VERI_PYTEST_WORKERS unset, a leg registers its own worker count in the VERI_PYTEST_LEGS registry while its pytest sessions run and removes its entry when it finishes, whether pytest passed or failed, so a leg that starts after it finished takes every core again; pinned in-process (a small case) with a fake core count, a spy on pytest.main that reads the registry while it runs, and a registry under tmp_path ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 97 | 27 | 52 | 9211 | 743617 | 97468 | 0.41 | 398 | unknown | 1/5 | nothing-left |  |  | full |
| A registry entry whose pid no longer answers kill -0 (a leg that died without unregistering) is ignored and holds no share: on a fake 16 cores, a leg starting beside only a stale 16-worker entry gets 16; pinned in-process (a small case) by a case with a stale entry ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 167 | 33 | 64 | 10085 | 866721 | 127774 | 0.60 | 539 | 1/2 | 0/5 | structural-owed |  |  | full |
| A registry entry whose pid is alive but owned by another user (kill -0 raises PermissionError) still answers kill -0 and holds its share: on a fake 16 cores, a leg starting beside only such a 16-worker entry gets 1; pinned in-process (a small case) with os.kill faked to raise PermissionError for that pid ⟦added⟧ ⟦criterion 2⟧ | 9 | 4 | 0 | 0 | 0 | 0 | 158 | 41 | 78 | 11409 | 1095194 | 112067 | 0.50 | 526 | unknown | 0/5 | nothing-structural |  |  | full |
| A set VERI_PYTEST_WORKERS is used as given, as today, even beside registered legs that hold every core: on a fake 16 cores with a live 16-worker entry registered, VERI_PYTEST_WORKERS=3 hands pytest -n 3; pinned in-process (a small case) ⟦criterion 3⟧ | 7 | 2 | 0 | 0 | 0 | 0 | 111 | 28 | 56 | 8777 | 731255 | 122601 | 0.47 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| With VERI_PYTEST_WORKERS unset, the leg reads the registry of running legs in the directory VERI_PYTEST_LEGS names (one entry per running leg: its pid and its worker count) and takes only the cores the registered legs leave free, at least 1: on a fake 16 cores a leg starting beside one registered 16-worker leg gets 1, and with two legs registered at 8 each a third gets 1; pinned in-process (a small case) with a fake core count and a fake registry under tmp_path ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 64 | 0.09 |
| With VERI_PYTEST_WORKERS and VERI_PYTEST_LEGS both unset, the leg reads and registers in a default registry directory every leg one user starts on the machine shares (under tempfile.gettempdir(), its name carrying the user id), exactly as it does in a named one, so legs nobody configured still share the cores: on a fake 16 cores with one live 16-worker entry in that default directory a leg gets 1; pinned in-process (a small case) with tempfile.gettempdir faked to a directory under tmp_path ⟦added⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 54 | 0.09 |
| With VERI_PYTEST_WORKERS unset, a leg registers its own worker count in the VERI_PYTEST_LEGS registry while its pytest sessions run and removes its entry when it finishes, whether pytest passed or failed, so a leg that starts after it finished takes every core again; pinned in-process (a small case) with a fake core count, a spy on pytest.main that reads the registry while it runs, and a registry under tmp_path ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 72 | 0.10 |
| A registry entry whose pid no longer answers kill -0 (a leg that died without unregistering) is ignored and holds no share: on a fake 16 cores, a leg starting beside only a stale 16-worker entry gets 16; pinned in-process (a small case) by a case with a stale entry ⟦criterion 2⟧ | 1 | 0/5 | structural-owed | PASS | 0 | 72 | 0.09 |
| A registry entry whose pid is alive but owned by another user (kill -0 raises PermissionError) still answers kill -0 and holds its share: on a fake 16 cores, a leg starting beside only such a 16-worker entry gets 1; pinned in-process (a small case) with os.kill faked to raise PermissionError for that pid ⟦added⟧ ⟦criterion 2⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 57 | 0.09 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 1/10 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 0 | 22 | 16 | 22 | 22 | 20 | 17 | 18 | 19 | 17 | 17 | 21 | 16 | 23 | 17 | 18 | 19 | 27 | 16 | 15 | 15 | 17 | 17 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| affected | 100 | 44 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 15 | 12 | 11 | 12 | 12 | 11 | 11 | 13 | 12 | 12 | 12 | 12 | 12 | 19 | 15 | 11 | 12 | 12 | 12 | 12 | 11 | 11 | 13 | 11 | 11 | 13 | 13 | 48 | 12 |
| target | 6 | 7 | 14 | 7 | 12 | 11 | 11 | 9 | 12 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 198 | 382 | 62909 | 5192064 | 768260 | 3.26 |
