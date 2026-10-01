### 📊 Metrics — issue 627

Wall time for the issue: 3146 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 8 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/641.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 24 | 19 | 2 | 4 | 1567 | 59646 | 38125 | 0.35 |
| cover | 5 | 0 | 0 | 0 | 254 | 63 | 20 | 40 | 5226 | 781580 | 189184 | 1.77 |
| transform | 11 | 5 | 0 | 0 | 3019 | 240 | 64 | 128 | 21363 | 2739553 | 432877 | 4.44 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Move Function: `documents` leaves `solvable-issues.sh` for a new `skills/tdd/scripts/lib/json_documents.py`, written complete (`documents(text)` — the documents in order, unflattened, skipping whitespace before each and at the end — and `items(text)` — their elements as one list), and `solvable-issues.sh` imports it via `PYTHONPATH` set to `lib`. Predicate: `test -f skills/tdd/scripts/lib/json_documents.py && ! grep -q raw_decode skills/tdd/scripts/solvable-issues.sh` ⟦criterion 2⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 103 | 26 | 52 | 9069 | 1143077 | 160045 | 1.69 | 1299 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call in `invisible-work.sh`: its copy of `documents` goes, and it imports `json_documents`. Predicate: `! grep -q raw_decode skills/tdd/scripts/invisible-work.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 53 | 14 | 28 | 4187 | 568176 | 114217 | 1.11 | 235 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call in `workqueue.sh`: its inline decode loop goes, and it imports `json_documents`. Predicate: `! grep -q raw_decode skills/tdd/scripts/workqueue.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 46 | 14 | 28 | 3924 | 564085 | 113951 | 1.10 | 135 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call in `parallel-conductors.sh`: its inline decode loop goes, and it imports `json_documents`. Predicate: `! grep -q raw_decode skills/tdd/scripts/parallel-conductors.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 47 | 15 | 30 | 4108 | 612492 | 113966 | 1.12 | 300 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call in `wait-ci.sh`: its `docs(text)` goes from both programs built on `$json_docs`, and they import `json_documents`'s `documents`. Predicate: `! grep -q raw_decode skills/tdd/scripts/wait-ci.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 54 | 15 | 30 | 5301 | 633303 | 119882 | 1.19 | 291 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 9 | 546 | 603 | 599 | 31 | 30 | 31 | 31 | 11 | 11 | 12 | 11 | 53 | 52 | 52 | 52 | 59 | 93 | 38 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 86 | 172 | 28156 | 3580779 | 660186 | 6.56 |
