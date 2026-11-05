### 📊 Metrics — issue 2847

Wall time for the issue: 1873 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 16 planned.
Outcome: the run bailed — no-verdict, a system failure.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $2.83 over 55 turns, in 1 sessions, on opus (estimate).
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 90470 tokens, largest 179065 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.58 | 90470 |
| 2 | $0.07 | 97508 |
| 3 | $0.04 | 99976 |
| 4 | $0.02 | 100435 |
| 5 | $0.04 | 102303 |
| 6 | $0.04 | 104185 |
| 7 | $0.02 | 104495 |
| 8 | $0.02 | 104796 |
| 9 | $0.02 | 105031 |
| 10 | $0.02 | 105327 |
| 11 | $0.03 | 106023 |
| 12 | $0.02 | 106310 |
| 13 | $0.12 | 119052 |
| 14 | $0.03 | 120075 |
| 15 | $0.04 | 122562 |
| 16 | $0.04 | 124307 |
| 17 | $0.04 | 125998 |
| 18 | $0.03 | 127043 |
| 19 | $0.04 | 128514 |
| 20 | $0.03 | 129145 |
| 21 | $0.03 | 130046 |
| 22 | $0.08 | 137142 |
| 23 | $0.07 | 141843 |
| 24 | $0.03 | 142648 |
| 25 | $0.03 | 143138 |
| 26 | $0.03 | 143553 |
| 27 | $0.03 | 143809 |
| 28 | $0.03 | 144488 |
| 29 | $0.04 | 145834 |
| 30 | $0.04 | 146770 |
| 31 | $0.04 | 147678 |
| 32 | $0.09 | 155751 |
| 33 | $0.04 | 157178 |
| 34 | $0.04 | 158484 |
| 35 | $0.04 | 158944 |
| 36 | $0.04 | 159760 |
| 37 | $0.04 | 160312 |
| 38 | $0.04 | 161185 |
| 39 | $0.04 | 161907 |
| 40 | $0.05 | 163561 |
| 41 | $0.04 | 164322 |
| 42 | $0.06 | 167327 |
| 43 | $0.04 | 168187 |
| 44 | $0.04 | 168417 |
| 45 | $0.04 | 168849 |
| 46 | $0.04 | 169347 |
| 47 | $0.04 | 169997 |
| 48 | $0.04 | 170540 |
| 49 | $0.04 | 171410 |
| 50 | $0.04 | 171860 |
| 51 | $0.04 | 172262 |
| 52 | $0.04 | 173053 |
| 53 | $0.04 | 173419 |
| 54 | $0.04 | 174300 |
| 55 | $0.07 | 179065 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 30 | 26 | 5 | 10 | 3077 | 144135 | 38710 | 0.14 |
| red | 8 | 2 | 1 | 0 | 273 | 122 | 36 | 68 | 12386 | 961841 | 161842 | 0.75 |
| green | 4 | 1 | 1 | 0 | 346 | 70 | 24 | 46 | 7144 | 717462 | 73896 | 0.33 |
| refactor | 1 | 0 | 0 | 0 | 10 | 7 | 3 | 6 | 478 | 83315 | 16949 | 0.06 |
| pin | 4 | 2 | 0 | 0 | 87 | 47 | 14 | 28 | 4042 | 389566 | 47535 | 0.20 |
| red-missing | 1 | 0 | 0 | 0 | 37 | 29 | 6 | 12 | 2338 | 186859 | 19190 | 0.09 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 10 | 6 | 2 | 0 | 482 | 145 | 41 | 78 | 14062 | 1115668 | 159297 | 0.65 |
| developer | claude-opus-5-5 | 2 | 0 | 0 | 0 | 55 | 41 | 10 | 20 | 4443 | 267404 | 71732 | 0.38 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 246 | 115 | 37 | 72 | 10960 | 1100106 | 127093 | 0.54 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 161 | 0.48 | 65 | 0.13 |
| green | 0 | 0.00 | 145 | 0.15 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 46 | 0.09 |
| red-missing | 0 | 0.00 | 37 | 0.09 |
| verify-pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `VERI_BASELINE_FULL_TIER` set to any value but `run` or `reuse` makes `run-conductor.sh` exit 2 at launch, before any cycle, through a `tunables.TABLE` entry, its one stderr line naming the variable and the value; the Red's case goes in `skills/tdd/scripts/tests/py/unit/test_tunables.py` ⟦criterion 1⟧ | 7 | 2 | 1 | 0 | 0 | 0 | 107 | 35 | 68 | 11108 | 999406 | 149561 | 0.71 | 524 | 1/2 | 0/5 | nothing-left |  |  | full |
| `VERI_BASELINE_FULL_TIER` unset, read through `tunables.resolve`, resolves to `run` with no error; one case in `skills/tdd/scripts/tests/py/unit/test_tunables.py` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 7 | 14 | 2380 | 194720 | 32538 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |
| `VERI_BASELINE_FULL_TIER=reuse`, read through `tunables.resolve`, resolves to `reuse` with no error; one case in `skills/tdd/scripts/tests/py/unit/test_tunables.py` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 27 | 8 | 16 | 2268 | 225660 | 32674 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| A new `skills/tdd/scripts/full-tier-time.sh` (a `/bin/sh` shim over a new `skills/tdd/scripts/veri/full_tier_time.py`, with a usage line `usage: full-tier-time.sh [--record <seconds>] <command>` and exit 2 when called with no argument) asked for a command that has no record prints nothing and exits 3; one case in a new `skills/tdd/scripts/tests/py/unit/test_full_tier_time.py` driving the CLI in-process with `run_cli` ⟦criterion 2⟧ | 7 | 1 | 1 | 0 | 0 | 0 | 118 | 33 | 62 | 10632 | 919257 | 104639 | 0.46 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `VERI_BASELINE_FULL_TIER` set to any value but `run` or `reuse` makes `run-conductor.sh` exit 2 at launch, before any cycle, through a `tunables.TABLE` entry, its one stderr line naming the variable and the value; the Red's case goes in `skills/tdd/scripts/tests/py/unit/test_tunables.py` ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 10 | 0.06 |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 2 | 4 | 24 | 31 | 4 | 3 | 3 | 3 | 3 | 3 | 3 |  |  |  |  |  |  |
| fast | 30 | 36 | 28 | 30 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 4 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 88 | 170 | 29465 | 2483178 | 358122 | 4.39 (estimate) |
