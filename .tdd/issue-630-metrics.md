### 📊 Metrics — issue 630

Wall time for the issue: 1759 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: -1 s, excluded from it.
Steps done: 3 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/648.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 13 | 2 | 4 | 1404 | 58961 | 37415 | 0.34 |
| cover | 3 | 0 | 0 | 0 | 106 | 39 | 13 | 26 | 3311 | 515825 | 112165 | 1.07 |
| transform | 6 | 3 | 0 | 0 | 669 | 132 | 39 | 78 | 13303 | 1691457 | 235685 | 2.49 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 4 | 4 | 0 | 0 | 318 | 66 | 17 | 34 | 6630 | 662983 | 150062 | 1.47 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 476 | 118 | 37 | 74 | 11388 | 1603260 | 235203 | 2.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Function: the result-record scan in `harvest-usage.sh`'s `closing_result` moves into a new `skills/tdd/scripts/lib/leaf_log.py` as `result_records(lines)` — every line that starts with `{` (after stripping) and parses as a JSON object whose `type` is `result`, in log order — and `harvest-usage.sh` imports it via `PYTHONPATH` set to `lib`, keeping its own "last record wins" selection. Predicate: `test -f skills/tdd/scripts/lib/leaf_log.py && grep -q leaf_log skills/tdd/scripts/harvest-usage.sh && ! grep -q '== "result"' skills/tdd/scripts/harvest-usage.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 56 | 18 | 36 | 5573 | 771119 | 116944 | 1.20 | 173 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call in `supervise.sh`: `terminal_outcome`'s inline scan goes, it imports `leaf_log`'s `result_records` and keeps its "last record wins" selection and its `success` / `failure` / exit 1 answers. Predicate: `grep -q leaf_log skills/tdd/scripts/supervise.sh && ! grep -q '== "result"' skills/tdd/scripts/supervise.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 56 | 18 | 36 | 5411 | 766214 | 114838 | 1.18 | 354 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call in `extract-result.sh`: its inline scan goes, it imports `leaf_log`'s `result_records` over the stdin text and keeps its own selection — the last record carrying a `result` key, preferring the newest one whose text has a `VERDICT:` line — and its passthrough when there is none. Predicate: `grep -q leaf_log skills/tdd/scripts/extract-result.sh && ! grep -q '== "result"' skills/tdd/scripts/extract-result.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 59 | 16 | 32 | 5630 | 669949 | 116068 | 1.18 | 369 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 6 | 22 | 16 | 2 | 46 | 128 | 22 | 46 | 1 | 21 | 74 | 81 | 1 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 54 | 108 | 18018 | 2266243 | 385265 | 3.90 |
