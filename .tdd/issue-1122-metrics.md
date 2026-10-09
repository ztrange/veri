### 📊 Metrics — issue 1122

Wall time for the issue: 2414 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1237.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 13 | 9 | 2 | 4 | 1307 | 55928 | 37297 | 0.17 |
| cover | 2 | 0 | 0 | 0 | 788 | 60 | 15 | 30 | 6310 | 703812 | 87617 | 0.97 |
| transform | 4 | 2 | 0 | 0 | 293 | 112 | 28 | 56 | 11635 | 1263776 | 162368 | 1.45 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 162 | 41 | 11 | 22 | 4522 | 406083 | 111782 | 0.57 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 932 | 140 | 34 | 68 | 14730 | 1617433 | 175500 | 2.02 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Function: orchestrate.py's `_watch` keeps its loop, its trailing-newline stop, its `context` print and its `return` on a breach, and moves the budget rule itself into a pure function in the new `skills/tdd/scripts/veri/context_budget.py`, which it calls. Predicate: `test -f skills/tdd/scripts/veri/context_budget.py && ! grep -qE '^(import|from) (os|sys|signal|subprocess)\b' skills/tdd/scripts/veri/context_budget.py && ! grep -q 'cache_creation_input_tokens' skills/tdd/scripts/veri/orchestrate.py && grep -qE 'from \.?context_budget import' skills/tdd/scripts/veri/orchestrate.py` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 80 | 20 | 40 | 8394 | 907022 | 122275 | 1.17 | 186 | n/a | n/a | n/a |  |  | full |
| Substitute Algorithm: parallel_conductors.py's `_watch_context` drops its own copy of the rule — the `CACHE_READ` and `CACHE_CREATION` regexes and the inline arm/check — and calls `context_budget.py`'s function, keeping its `context` print, its per-check read of `_ctx_budget()`, its SIGTERM to the supervisor on a breach and its `stopped` flag, leaving the token-count parse in `context_budget.py` alone of the two modules and their shared one. Predicate: `! grep -qE 'CACHE_READ|CACHE_CREATION|cache_creation_input_tokens' skills/tdd/scripts/veri/parallel_conductors.py && grep -qE 'from \.?context_budget import' skills/tdd/scripts/veri/parallel_conductors.py && ! grep -q 'cache_creation_input_tokens' skills/tdd/scripts/veri/orchestrate.py && grep -q 'cache_creation_input_tokens' skills/tdd/scripts/veri/context_budget.py` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 92 | 23 | 46 | 9551 | 1060566 | 127710 | 1.26 | 974 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 9 | 8 | 34 | 1 | 1 | 38 | 30 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 45 | 90 | 19252 | 2023516 | 287282 | 2.60 |
