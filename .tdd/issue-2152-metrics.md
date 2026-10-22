### 📊 Metrics — issue 2152

Wall time for the issue: 1781 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2165.
Lane: ready-for-agent
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.78 over 39 turns, in 1 sessions.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.56 | 86611 |
| 2 | $0.03 | 87770 |
| 3 | $0.03 | 89726 |
| 4 | $0.02 | 89994 |
| 5 | $0.02 | 90367 |
| 6 | $0.02 | 90727 |
| 7 | $0.02 | 91052 |
| 8 | $0.02 | 91784 |
| 9 | $0.03 | 93022 |
| 10 | $0.03 | 95005 |
| 11 | $0.03 | 96845 |
| 12 | $0.02 | 97088 |
| 13 | $0.03 | 97950 |
| 14 | $0.03 | 98975 |
| 15 | $0.02 | 99508 |
| 16 | $0.03 | 100303 |
| 17 | $0.02 | 100895 |
| 18 | $0.03 | 101603 |
| 19 | $0.03 | 102260 |
| 20 | $0.11 | 113125 |
| 21 | $0.03 | 113866 |
| 22 | $0.03 | 114481 |
| 23 | $0.03 | 115051 |
| 24 | $0.03 | 116057 |
| 25 | $0.09 | 124673 |
| 26 | $0.03 | 125494 |
| 27 | $0.03 | 125832 |
| 28 | $0.03 | 126609 |
| 29 | $0.04 | 128938 |
| 30 | $0.03 | 129648 |
| 31 | $0.03 | 130087 |
| 32 | $0.03 | 130754 |
| 33 | $0.03 | 131045 |
| 34 | $0.03 | 131379 |
| 35 | $0.03 | 131683 |
| 36 | $0.03 | 132103 |
| 37 | $0.03 | 132648 |
| 38 | $0.03 | 132987 |
| 39 | $0.03 | 133327 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 23 | 15 | 3 | 6 | 1037 | 61562 | 31495 | 0.10 |
| diff | 2 | 1 | 0 | 0 | 197 | 26 | 10 | 20 | 2292 | 243908 | 41604 | 0.15 |
| red | 2 | 0 | 0 | 0 | 69 | 45 | 9 | 18 | 4562 | 253801 | 31630 | 0.15 |
| pin | 2 | 2 | 0 | 0 | 94 | 32 | 7 | 12 | 2002 | 148074 | 25830 | 0.10 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 216 | 62 | 15 | 28 | 4220 | 339388 | 69386 | 0.25 |
| developer | claude-sonnet-5-5 | 3 | 0 | 0 | 0 | 167 | 56 | 14 | 28 | 5673 | 367957 | 61173 | 0.25 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| BAIL.md's `no-verdict` entry names exactly the scripts whose exit 2 bails `no-verdict` today — `verify.sh` / `run-verdict.sh` (a verifier with no verdict), `grade-prose.sh` (the Draft PR regrade), the ⟦skill-edit⟧ runner (`skill-edit-step.sh`), `resume-clean.sh`, `rebase-onto-default.sh` and `cover-outcome.sh` — and calls it a **system** failure; only that entry of skills/tdd/BAIL.md changes ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 10 | 20 | 2292 | 243908 | 41604 | 0.15 | 275 | n/a | n/a | n/a |  |  | full |
| A small unit case in skills/tdd/scripts/tests/py/unit/test_bail_no_verdict_sources.py holds the fixed list of no-verdict sources (verify.sh, run-verdict.sh, grade-prose.sh, skill-edit-step.sh, resume-clean.sh, rebase-onto-default.sh, cover-outcome.sh) in one module-level constant, and passes only when skills/tdd/BAIL.md's `no-verdict` entry names every script on that list, names no `.sh` script off it, and calls the cause a **system** failure; the module docstring says a new `no-verdict` source is added to the list and to BAIL.md together; no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 43 | 8 | 14 | 3527 | 184705 | 29170 | 0.13 | unknown | unknown | unknown | unknown |  |  | pin |
| In the same suite skills/tdd/scripts/tests/py/unit/test_bail_no_verdict_sources.py, planted copies of the `no-verdict` entry — one dropping a listed script, one naming an extra script not on the list, one saying "process" in place of "system" — are each refused by the guard's check, which reads the one fixed list; small unit cases, no production change ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 34 | 8 | 16 | 3037 | 217170 | 28290 | 0.12 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| fast | 17 | 17 |  |  |
| affected | 64 | 62 | 2 | 3 |
| target | 11 | 11 | 13 | 11 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 29 | 56 | 9893 | 707345 | 130559 | 0.50 |
