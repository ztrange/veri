### 📊 Metrics — issue 1720

Wall time for the issue: 2842 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1921.
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $3.60 over 93 turns, in 1 sessions.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.54 | 84803 |
| 2 | $0.02 | 85285 |
| 3 | $0.02 | 86236 |
| 4 | $0.02 | 86615 |
| 5 | $0.02 | 87520 |
| 6 | $0.02 | 87880 |
| 7 | $0.02 | 88183 |
| 8 | $0.02 | 88443 |
| 9 | $0.02 | 88651 |
| 10 | $0.02 | 88908 |
| 11 | $0.02 | 89554 |
| 12 | $0.03 | 91057 |
| 13 | $0.03 | 91906 |
| 14 | $0.03 | 93510 |
| 15 | $0.06 | 98294 |
| 16 | $0.03 | 99530 |
| 17 | $0.03 | 101044 |
| 18 | $0.04 | 103212 |
| 19 | $0.03 | 103825 |
| 20 | $0.03 | 104449 |
| 21 | $0.03 | 105311 |
| 22 | $0.04 | 107227 |
| 23 | $0.04 | 109315 |
| 24 | $0.02 | 109619 |
| 25 | $0.03 | 110356 |
| 26 | $0.03 | 110758 |
| 27 | $0.03 | 111096 |
| 28 | $0.02 | 111338 |
| 29 | $0.03 | 112036 |
| 30 | $0.02 | 112281 |
| 31 | $0.03 | 113643 |
| 32 | $0.03 | 114569 |
| 33 | $0.03 | 115282 |
| 34 | $0.03 | 115804 |
| 35 | $0.03 | 116210 |
| 36 | $0.03 | 116794 |
| 37 | $0.03 | 117090 |
| 38 | $0.03 | 117820 |
| 39 | $0.03 | 118436 |
| 40 | $0.03 | 118681 |
| 41 | $0.03 | 119607 |
| 42 | $0.03 | 120190 |
| 43 | $0.03 | 120597 |
| 44 | $0.08 | 128025 |
| 45 | $0.03 | 128387 |
| 46 | $0.03 | 129355 |
| 47 | $0.03 | 130102 |
| 48 | $0.03 | 130646 |
| 49 | $0.03 | 131043 |
| 50 | $0.03 | 131940 |
| 51 | $0.03 | 132663 |
| 52 | $0.03 | 133073 |
| 53 | $0.03 | 133593 |
| 54 | $0.03 | 134362 |
| 55 | $0.03 | 135123 |
| 56 | $0.03 | 135694 |
| 57 | $0.03 | 136161 |
| 58 | $0.03 | 137039 |
| 59 | $0.04 | 138244 |
| 60 | $0.03 | 138916 |
| 61 | $0.04 | 139808 |
| 62 | $0.04 | 141014 |
| 63 | $0.04 | 141801 |
| 64 | $0.04 | 142882 |
| 65 | $0.03 | 143265 |
| 66 | $0.04 | 144072 |
| 67 | $0.04 | 145206 |
| 68 | $0.04 | 146661 |
| 69 | $0.04 | 147398 |
| 70 | $0.04 | 149068 |
| 71 | $0.04 | 149787 |
| 72 | $0.04 | 151081 |
| 73 | $0.04 | 151808 |
| 74 | $0.04 | 152934 |
| 75 | $0.04 | 154363 |
| 76 | $0.05 | 156911 |
| 77 | $0.04 | 157597 |
| 78 | $0.03 | 157866 |
| 79 | $0.04 | 158593 |
| 80 | $0.05 | 160236 |
| 81 | $0.04 | 160947 |
| 82 | $0.05 | 162544 |
| 83 | $0.04 | 163351 |
| 84 | $0.04 | 164650 |
| 85 | $0.04 | 165403 |
| 86 | $0.05 | 167255 |
| 87 | $0.04 | 167558 |
| 88 | $0.04 | 167862 |
| 89 | $0.04 | 168141 |
| 90 | $0.04 | 168494 |
| 91 | $0.04 | 168925 |
| 92 | $0.04 | 169379 |
| 93 | $0.04 | 169750 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 10 | 2 | 4 | 1137 | 29975 | 31923 | 0.09 |
| red | 9 | 4 | 0 | 0 | 207 | 153 | 43 | 82 | 15967 | 1167474 | 164058 | 0.69 |
| green | 10 | 4 | 1 | 0 | 642 | 181 | 50 | 96 | 14818 | 1341075 | 148303 | 0.76 |
| refactor | 8 | 4 | 0 | 0 | 181 | 78 | 23 | 42 | 4143 | 518489 | 99987 | 0.34 |
| pin | 1 | 1 | 0 | 0 | 19 | 13 | 4 | 8 | 1059 | 103276 | 12550 | 0.05 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 15 | 14 | 1 | 0 | 500 | 186 | 52 | 100 | 15086 | 1274076 | 203373 | 0.79 |
| developer | claude-sonnet-5-5 | 12 | 0 | 0 | 0 | 314 | 183 | 53 | 100 | 17635 | 1412987 | 201744 | 0.82 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 248 | 66 | 17 | 32 | 4403 | 473226 | 51704 | 0.33 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 398 | 0.43 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `watch-runs.sh` (a `/bin/sh` shim exec'ing `python3` on a new `veri/watch_runs.py`, its usage line naming only optional options, listed in `SCRIPTS.md` as its declared caller) prints `exited <issue> <state>` and exits 0 when a conductor that was live when it started exits, `<state>` being the first word of that run's state as `status.sh` reports it (`done`, `bailed`, `stopped` or `stale`); pinned by a small case with the live-conductor listing, the run state and the wait injected in-process, no real process and no real sleep ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 156 | 44 | 80 | 12784 | 1145460 | 152115 | 0.73 | 628 | 1/2 | 0/5 | nothing-left |  |  | full |
| `watch-runs.sh --target <N>` prints `slot-free <live>/<N> next <issue>` and exits 0 when fewer than N conductors are live and `solvable-issues.sh --not-running` lists an issue, `<issue>` being the first one listed; pinned by a small case with the live-conductor listing and the solvable listing injected in-process ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 78 | 21 | 38 | 6040 | 489049 | 79111 | 0.31 | 232 | unknown | 0/5 | nothing-left |  |  | full |
| `watch-runs.sh --max-wait <seconds>` prints `timeout` and exits 3 when nothing actionable happened within that wait; pinned by a small case driven by an injected clock, no real sleep ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 67 | 22 | 44 | 6526 | 585374 | 80914 | 0.33 | 234 | unknown | 0/5 | nothing-left |  |  | full |
| While nothing actionable happens `watch-runs.sh` prints nothing: across several polls in which no live conductor exits and no slot frees, stdout stays empty until an actionable event or the timeout line; pinned by a small case with injected listings and clock ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 12 | 24 | 4667 | 354706 | 31476 | 0.16 | unknown | unknown | unknown | unknown |  |  | pin |
| A `--target` or `--max-wait` whose value is not a whole number ≥ 1 (`0`, `-1`, `abc`, empty, or missing) makes `watch-runs.sh` exit 2 with a usage line on stderr before any wait or listing is taken; pinned by a small case ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 80 | 21 | 42 | 5970 | 555725 | 81282 | 0.32 | 265 | unknown | 0/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `watch-runs.sh` (a `/bin/sh` shim exec'ing `python3` on a new `veri/watch_runs.py`, its usage line naming only optional options, listed in `SCRIPTS.md` as its declared caller) prints `exited <issue> <state>` and exits 0 when a conductor that was live when it started exits, `<state>` being the first word of that run's state as `status.sh` reports it (`done`, `bailed`, `stopped` or `stale`); pinned by a small case with the live-conductor listing, the run state and the wait injected in-process, no real process and no real sleep ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 42 | 0.09 |
| `watch-runs.sh --target <N>` prints `slot-free <live>/<N> next <issue>` and exits 0 when fewer than N conductors are live and `solvable-issues.sh --not-running` lists an issue, `<issue>` being the first one listed; pinned by a small case with the live-conductor listing and the solvable listing injected in-process ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 42 | 0.09 |
| `watch-runs.sh --max-wait <seconds>` prints `timeout` and exits 3 when nothing actionable happened within that wait; pinned by a small case driven by an injected clock, no real sleep ⟦criterion 3⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 43 | 0.08 |
| A `--target` or `--max-wait` whose value is not a whole number ≥ 1 (`0`, `-1`, `abc`, empty, or missing) makes `watch-runs.sh` exit 2 with a usage line on stderr before any wait or listing is taken; pinned by a small case ⟦criterion 5⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 54 | 0.08 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 0 | 68 | 1 | 68 | 0 | 65 | 2 | 1 | 2 | 2 | 2 | 2 | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 1 | 2 |
| fast | 19 | 18 | 17 | 17 | 18 | 17 | 17 | 17 | 17 | 18 | 19 | 18 | 17 | 19 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 122 | 232 | 37124 | 3160289 | 456821 | 1.93 |
