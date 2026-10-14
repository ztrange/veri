### 📊 Metrics — issue 1366

Wall time for the issue: 2358 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run bailed — ci-timeout, a system failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 13 | 2 | 4 | 1433 | 67767 | 44260 | 0.20 |
| diff | 4 | 2 | 0 | 0 | 448 | 145 | 34 | 66 | 15613 | 1856998 | 216679 | 1.21 |
| expand | 2 | 1 | 0 | 0 | 122 | 54 | 14 | 28 | 4409 | 699341 | 90588 | 0.48 |
| migrate | 2 | 1 | 0 | 0 | 181 | 54 | 15 | 30 | 4027 | 762516 | 92173 | 0.49 |
| contract-a | 4 | 1 | 1 | 0 | 300 | 117 | 29 | 56 | 11164 | 1479876 | 202447 | 1.37 |
| red | 3 | 1 | 0 | 0 | 88 | 70 | 18 | 34 | 8006 | 864597 | 150860 | 0.77 |
| pin | 1 | 1 | 0 | 0 | 26 | 19 | 4 | 8 | 1263 | 181198 | 47554 | 0.22 |
| green | 2 | 1 | 0 | 0 | 183 | 40 | 14 | 26 | 4347 | 663430 | 95403 | 0.49 |
| refactor | 2 | 1 | 0 | 0 | 96 | 27 | 13 | 24 | 3159 | 592626 | 93775 | 0.47 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 11 | 10 | 1 | 0 | 836 | 259 | 68 | 128 | 23667 | 3184640 | 525691 | 2.66 |
| developer | claude-sonnet-5-5 | 8 | 0 | 0 | 0 | 505 | 223 | 59 | 116 | 23363 | 3106123 | 402557 | 2.15 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 122 | 57 | 16 | 32 | 6391 | 877586 | 105491 | 0.88 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 122 | 0.48 |
| migrate | 0 | 0.00 | 181 | 0.49 |
| contract-a | 300 | 1.37 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Test-only step, changing no production file and green against today's code: the tests/py/test_dashboard.py cases that pin render-leaf-log.sh's argv or stdin (the /api/chatter cases for runs 54, 59, 61, 63/65 and 55) assert instead that /api/chatter answers the rendering of the stream-json lines of the leaf log the run's newest launch names, a non-stream-json line showing as the empty answer the renderer gives it; a reverted probe deleting dashboard.py:371's call to render-leaf-log.sh turns each rewritten case red; the commit lists only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 91 | 19 | 36 | 10712 | 1067646 | 116437 | 0.68 | 307 | n/a | n/a | n/a |  |  | full |
| dashboard's /api/chatter renders the current leaf's log by calling a function of veri/render_leaf_log.py that takes the log text and returns the exit code and the rendering, instead of starting render-leaf-log.sh; the shim render-leaf-log.sh stays for SKILL.md ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 14 | 28 | 4409 | 699341 | 90588 | 0.48 | unknown | unknown | unknown | unknown |  |  | full |
| dashboard's /api/chatter renders the current leaf's log by calling a function of veri/render_leaf_log.py that takes the log text and returns the exit code and the rendering, instead of starting render-leaf-log.sh; the shim render-leaf-log.sh stays for SKILL.md ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 15 | 30 | 4027 | 762516 | 92173 | 0.49 | unknown | unknown | unknown | unknown |  |  | full |
| dashboard's /api/chatter renders the current leaf's log by calling a function of veri/render_leaf_log.py that takes the log text and returns the exit code and the rendering, instead of starting render-leaf-log.sh; the shim render-leaf-log.sh stays for SKILL.md ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 4 | 1 | 1 | 0 | 0 | 0 | 117 | 29 | 56 | 11164 | 1479876 | 202447 | 1.37 | unknown | 1/2 | unknown | unknown |  |  | full |
| dashboard's /api/chatter gives its full answer — exit code, stdout, stderr, and the files and events render-leaf-log.sh writes — when starting render-leaf-log.sh as a process is refused at the process boundary, by calling render_leaf_log's function in-process (dashboard.py:371); the case that refuses that start is its own test, since the migrate phase freezes tests ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 9 | 18 | 3771 | 425001 | 96488 | 0.47 | unknown | unknown | unknown | unknown |  |  | pin |
| No test of dashboard fakes render-leaf-log.sh at the process boundary any longer: each such test is rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 15 | 30 | 4901 | 789352 | 100242 | 0.53 | 217 | n/a | n/a | n/a |  |  | full |
| When a leaf log holds a line that is JSON but not a record render_leaf_log can render (42, {"message":{"content":"hi"}}, a tool_use with no name), /api/chatter still answers {"chatter": ""} with a 200 and prints nothing to the dashboard's stderr, and dashboard.py's rendered_log gets the same (2, "") answer the entry point gave; pinned by a /api/chatter case for each of the three lines ⟦added⟧ ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 118 | 40 | 74 | 13004 | 1876850 | 291104 | 1.48 | 454 | unknown | 0/5 | nothing-structural |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When a leaf log holds a line that is JSON but not a record render_leaf_log can render (42, {"message":{"content":"hi"}}, a tool_use with no name), /api/chatter still answers {"chatter": ""} with a 200 and prints nothing to the dashboard's stderr, and dashboard.py's rendered_log gets the same (2, "") answer the entry point gave; pinned by a /api/chatter case for each of the three lines ⟦added⟧ ⟦criterion 4⟧ | 1 | 0/5 | nothing-structural | PASS | 0 | 96 | 0.47 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 51 | 52 | 53 | 53 | 52 | 52 | 53 | 53 | 52 | 62 | 60 | 60 |  |  |  |  |  |  |  |  |  |  |
| affected | 1 | 3 | 0 | 0 | 53 | 5 | 0 | 5 | 1 | 1 | 1 | 1 | 0 | 5 | 0 | 4 | 0 | 1 | 0 | 2 | 2 | 1 |
| target | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 143 | 276 | 53421 | 7168349 | 1033739 | 5.69 |
