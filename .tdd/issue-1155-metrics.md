### 📊 Metrics — issue 1155

Wall time for the issue: 1569 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 5 planned.
Outcome: the run bailed — untestable-criterion, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 12 | 9 | 1 | 2 | 1092 | 10759 | 33617 | 0.15 |
| red | 5 | 1 | 0 | 0 | 238 | 205 | 39 | 74 | 19843 | 1915822 | 249384 | 2.60 |
| green | 2 | 1 | 0 | 0 | 109 | 48 | 14 | 28 | 4751 | 726721 | 97593 | 0.84 |
| refactor | 2 | 1 | 0 | 0 | 50 | 19 | 7 | 14 | 1787 | 265953 | 80030 | 0.56 |
| pin | 2 | 2 | 0 | 0 | 204 | 67 | 20 | 40 | 8263 | 1000044 | 89913 | 0.64 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 317 | 112 | 34 | 68 | 13266 | 1537248 | 242964 | 1.41 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 296 | 236 | 47 | 90 | 22470 | 2382051 | 307573 | 3.39 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 82 | 0.67 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| develop-red | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Through the entry point, `detach-command.sh wait <name>` with VERI_POLL set to `abc` or `-1` exits 2 before any polling round, writing exactly one stderr line that names VERI_POLL and the value and nothing on stdout, and never pauses or loops; the pytest case pinning the per-round busy poll for those values is retired with it ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 122 | 32 | 64 | 11935 | 1508353 | 269728 | 2.18 | 310 | unknown | 0/5 | nothing-left |  |  | full |
| Through the entry point, `detach-command.sh wait <name>` with VERI_POLL set to a value `sleep` accepted on main but that is not a plain non-negative decimal (`1e-1`, `0.1s`, `1m`) gets the same single refusal: exit 2 before any round, one stderr line naming VERI_POLL and the value ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 10 | 20 | 4886 | 430480 | 83470 | 0.68 | unknown | unknown | unknown | unknown |  |  | pin |
| `detach-command.sh wait <name>` with VERI_POLL unset or empty still pauses 1 second between rounds, and with `0` or `0.05` pauses exactly that long, with nothing on stderr ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 102 | 27 | 52 | 11465 | 1424500 | 109157 | 1.12 | unknown | unknown | unknown | unknown |  |  | pin |
| fix the CI failure: orchestrate.test.sh — FAIL - #1126 with SIGPIPE and SIGXFSZ at their defaults, a conductor still leads a new session whose pid orchestrate SIGTERMs, stdin /dev/null, stderr orchestrate's, SIGINT and SIGQUIT ignored (stderr carried an extra 'Terminated' line on the Linux runner) ⟦ci-repair⟧ ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 72 | 11 | 20 | 6358 | 545207 | 54565 | 0.67 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Through the entry point, `detach-command.sh wait <name>` with VERI_POLL set to `abc` or `-1` exits 2 before any polling round, writing exactly one stderr line that names VERI_POLL and the value and nothing on stdout, and never pauses or loops; the pytest case pinning the per-round busy poll for those values is retired with it ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 50 | 0.56 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 2 | 1 | 1 | 0 | 0 | 1 | 0 |  |  |  |  |  |
| fast | 24 | 23 | 23 |  |  |  |  |  |  |  |  |  |  |
| target | 1 | 1 | 5 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 81 | 158 | 35736 | 3919299 | 550537 | 4.80 |
