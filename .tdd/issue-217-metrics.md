### 📊 Metrics — issue 217

Wall time for the issue: 6786 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 12 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/480.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 21 | 16 | 2 | 4 | 1655 | 56570 | 40859 | 0.37 |
| red | 19 | 7 | 0 | 0 | 1051 | 779 | 145 | 276 | 73499 | 7198503 | 954902 | 10.55 |
| green | 22 | 7 | 4 | 0 | 3687 | 866 | 186 | 364 | 81791 | 8898304 | 870095 | 10.38 |
| refactor | 14 | 7 | 0 | 0 | 716 | 434 | 104 | 200 | 40367 | 4754962 | 621034 | 6.73 |
| pin | 5 | 5 | 0 | 0 | 359 | 141 | 31 | 60 | 13410 | 1321376 | 215443 | 2.26 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 2725 | 8.01 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| orchestrate.sh launches one conductor per issue solvable-issues.sh prints, each through run-conductor.sh with that issue number, and exits 0 once the solvable set is empty ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 276 | 61 | 114 | 26454 | 2791562 | 336355 | 3.78 | 936 | 1/2 | 0/5 | nothing-left |
| orchestrate.sh exits 2 without launching any conductor when solvable-issues.sh exits with anything other than 0 or 3, since then no answer about the solvable set could be obtained ⟦added⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 157 | 40 | 76 | 14240 | 1676412 | 247140 | 2.60 | 248 | unknown | 1/5 | structural-owed |
| orchestrate.sh computes the conductor's context as cache_read_input_tokens + cache_creation_input_tokens from each assistant event's usage in the launched stream, as the stream arrives, and never needs a closing result record to know it ⟦criterion 2⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 275 | 61 | 120 | 26597 | 2944408 | 333510 | 3.79 | 770 | 1/2 | 2/5 | nothing-structural |
| a conductor whose stream crosses VERI_CONDUCTOR_CTX_BUDGET mid-step is not stopped until a step-done is seen, and is stopped after it ⟦criterion 3⟧ | 10 | 3 | 2 | 0 | 0 | 0 | 495 | 89 | 172 | 47595 | 4497835 | 424673 | 5.25 | 1922 | 2/2 | 3/5 | structural-owed |
| a conductor whose stream never crosses VERI_CONDUCTOR_CTX_BUDGET is never stopped or restarted ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 74 | 13 | 24 | 7194 | 594882 | 97639 | 1.04 | unknown | unknown | unknown | unknown |
| VERI_CONDUCTOR_CTX_BUDGET is a whole token count read as ${VAR:-default} with a default of 120000, and a value that is not a whole number is refused with exit 2 before any conductor launches ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 199 | 47 | 94 | 19969 | 2229526 | 265199 | 2.97 | 415 | unknown | 2/5 | structural-owed |
| with VERI_CONDUCTOR_CTX_BUDGET unset, a conductor whose context crosses 120000 tokens is stopped after its next step-done, so the 120000 default is the budget in force ⟦added⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 60 | 14 | 26 | 5946 | 657226 | 97420 | 1.03 | unknown | unknown | unknown | unknown |
| a conductor stopped over budget is relaunched for the same issue through run-conductor.sh with the same argv, so it takes the ledger's resume path rather than re-planning ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 94 | 14 | 26 | 7450 | 658305 | 102020 | 1.10 | unknown | unknown | unknown | unknown |
| a conductor that exits 0 while its issue is still in the solvable set and its ledger still has an unchecked step is treated as unfinished, not done ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 68 | 13 | 24 | 6668 | 583869 | 97952 | 1.03 | unknown | unknown | unknown | unknown |
| an issue whose run wrote .tdd/parked/<n>.md is recorded as parked, its branch and ledger are left untouched, it is skipped on the next pass, and the next solvable issue is taken ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 215 | 47 | 92 | 16943 | 2209141 | 270558 | 2.95 | 384 | unknown | 1/5 | nothing-structural |
| run-conductor.sh and SKILL.md launched directly for one issue, with no orchestrator, behave as before: nothing the orchestrator adds is required by a direct /tdd run ⟦criterion 7⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 119 | 22 | 42 | 12281 | 1202386 | 113026 | 1.39 | unknown | unknown | unknown | unknown |
| CLAUDE.md's script and suite counts include orchestrate.sh and its suite ⟦criterion 8⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 188 | 45 | 90 | 17730 | 2127593 | 275982 | 2.99 | 756 | unknown | 0/5 | structural-owed |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s | run 51 s | run 52 s | run 53 s | run 54 s | run 55 s | run 56 s | run 57 s | run 58 s | run 59 s | run 60 s | run 61 s | run 62 s | run 63 s | run 64 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 0 | 80 | 50 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 0 | 0 | 1 | 4 | 4 | 1 | 43 | 4 | 1 | 5 | 5 | 4 | 5 | 5 | 5 | 6 | 6 | 0 | 50 | 6 | 6 | 5 | 6 | 5 | 6 | 6 | 7 | 8 | 7 | 6 | 6 | 0 | 6 | 7 | 7 | 38 | 0 | 1 | 1 | 0 | 74 | 83 | 10 | 85 | 0 | 86 |
| fast | 3 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 4 | 3 | 3 | 4 | 4 | 3 | 3 | 4 | 4 | 3 | 3 | 4 | 3 | 4 | 3 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 4 | 5 | 6 | 2 | 6 | 6 | 10 | 6 | 6 | 6 | 6 | 6 | 39 | 38 | 30 | 37 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| all | 377 | 377 | 381 | 381 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 468 | 904 | 210722 | 22229715 | 2702333 | 30.28 |
