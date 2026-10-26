### 📊 Metrics — issue 2447

Wall time for the issue: 1108 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 4 planned.
Outcome: the run bailed — revise-exhausted, a process failure.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.19 over 50 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88701 tokens, largest 149359 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88701 |
| 2 | $0.03 | 90855 |
| 3 | $0.03 | 92843 |
| 4 | $0.02 | 93315 |
| 5 | $0.02 | 93675 |
| 6 | $0.03 | 94694 |
| 7 | $0.02 | 95396 |
| 8 | $0.02 | 95728 |
| 9 | $0.02 | 96424 |
| 10 | $0.02 | 96753 |
| 11 | $0.04 | 99197 |
| 12 | $0.04 | 102275 |
| 13 | $0.03 | 103186 |
| 14 | $0.02 | 103564 |
| 15 | $0.03 | 104277 |
| 16 | $0.03 | 104830 |
| 17 | $0.02 | 105075 |
| 18 | $0.03 | 105745 |
| 19 | $0.03 | 106844 |
| 20 | $0.03 | 107598 |
| 21 | $0.04 | 109594 |
| 22 | $0.03 | 110441 |
| 23 | $0.03 | 111197 |
| 24 | $0.03 | 111912 |
| 25 | $0.03 | 112826 |
| 26 | $0.03 | 113603 |
| 27 | $0.03 | 114497 |
| 28 | $0.03 | 115220 |
| 29 | $0.03 | 115604 |
| 30 | $0.03 | 116586 |
| 31 | $0.03 | 117202 |
| 32 | $0.03 | 118569 |
| 33 | $0.04 | 121005 |
| 34 | $0.03 | 121708 |
| 35 | $0.03 | 122026 |
| 36 | $0.03 | 122890 |
| 37 | $0.04 | 124482 |
| 38 | $0.03 | 125374 |
| 39 | $0.03 | 126383 |
| 40 | $0.03 | 127505 |
| 41 | $0.03 | 128368 |
| 42 | $0.09 | 136403 |
| 43 | $0.05 | 138750 |
| 44 | $0.03 | 139581 |
| 45 | $0.04 | 140504 |
| 46 | $0.03 | 141240 |
| 47 | $0.04 | 143051 |
| 48 | $0.04 | 143992 |
| 49 | $0.04 | 145303 |
| 50 | $0.06 | 149359 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 917 | 0 | 33444 | 0.09 |
| red | 5 | 2 | 0 | 0 | 143 | 82 | 29 | 58 | 10547 | 934980 | 120140 | 0.50 |
| green | 8 | 1 | 3 | 0 | 535 | 185 | 46 | 88 | 15950 | 1384026 | 135711 | 0.92 |
| refactor | 1 | 0 | 0 | 0 | 6 | 3 | 2 | 4 | 152 | 50498 | 15639 | 0.05 |
| pin | 1 | 1 | 0 | 0 | 16 | 8 | 3 | 6 | 921 | 80698 | 16073 | 0.06 |
| exhausted | 1 | 0 | 0 | 0 | 15 | 13 | 3 | 6 | 1088 | 80604 | 15207 | 0.11 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 5 | 3 | 0 | 303 | 101 | 29 | 58 | 9721 | 828497 | 121341 | 0.48 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 192 | 91 | 30 | 58 | 10187 | 940434 | 118897 | 0.49 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 230 | 107 | 25 | 48 | 9667 | 761875 | 95976 | 0.75 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 36 | 0.14 |
| green | 0 | 0.00 | 389 | 0.78 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| exhausted | 0 | 0.00 | 15 | 0.11 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| A `.tdd/issue-<n>-tmpdir-skill-commit` record whose pid exists but belongs to another user (`os.kill(pid, 0)` raises `PermissionError`) does not stop a launch: `run-conductor.sh` gets past the sweep, the record and its directory are left in place, and the launch goes on; the case fails on the current code (a small in-process case faking only the `os.kill` boundary) ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 71 | 26 | 50 | 7157 | 778391 | 111198 | 0.43 | 350 | unknown | 0/5 | nothing-left |  |  | full |
| A tmpdir record whose pid is genuinely gone (`os.kill(pid, 0)` raises `ProcessLookupError`) still has its `veri-run-*` directory swept, so the fix does not turn the sweep off ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 28 | 10 | 20 | 3905 | 317977 | 37916 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |
| A `PermissionError` escaping a `veri/` entry point's `main` names the operation that raised it (the call, such as `os.kill`) in the refusal line `entry.py` prints, not only the exception class and message ⟦criterion 3⟧ | 9 | 1 | 3 | 0 | 0 | 0 | 192 | 47 | 92 | 17596 | 1434438 | 153656 | 1.04 | unknown | 2/2 | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| A `.tdd/issue-<n>-tmpdir-skill-commit` record whose pid exists but belongs to another user (`os.kill(pid, 0)` raises `PermissionError`) does not stop a launch: `run-conductor.sh` gets past the sweep, the record and its directory are left in place, and the launch goes on; the case fails on the current code (a small in-process case faking only the `os.kill` boundary) ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 6 | 0.05 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 17 | 18 | 21 | 20 | 1 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 21 | 1 | 1 | 1 |
| fast | 20 | 21 | 19 | 18 | 21 | 18 | 19 | 20 | 19 | 18 |  |  |  |  |  |  |
| target | 2 | 1 | 1 | 1 | 1 | 1 |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 84 | 164 | 29575 | 2530806 | 336214 | 1.72 |
