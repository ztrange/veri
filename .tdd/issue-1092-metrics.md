### 📊 Metrics — issue 1092

Wall time for the issue: 2053 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1395.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 2 | 4 | 1239 | 66047 | 43921 | 0.19 |
| cover | 3 | 0 | 0 | 0 | 115 | 90 | 19 | 38 | 7921 | 924524 | 140700 | 1.47 |
| transform | 5 | 2 | 0 | 0 | 293 | 172 | 40 | 78 | 17018 | 2076909 | 264473 | 2.42 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 126 | 45 | 14 | 28 | 5286 | 632630 | 133185 | 0.65 |
| developer | claude-opus-5-5 | 6 | 0 | 0 | 0 | 297 | 228 | 47 | 92 | 20892 | 2434850 | 315909 | 3.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Function: move tick_ledger.py's temp-file-beside-the-real-path-then-os.replace write into one helper `replace_ledger(path, data)` in veri/ledger.py and have tick_ledger.py call it, its behaviour on a symlinked ledger and on a failed write unchanged — predicate, run from skills/tdd/scripts: `grep -F 'def replace_ledger(' veri/ledger.py >/dev/null && grep -F 'ledger.replace_ledger(' veri/tick_ledger.py >/dev/null && ! grep -F 'mkstemp' veri/tick_ledger.py >/dev/null` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 75 | 19 | 38 | 7545 | 918103 | 136983 | 1.22 | 236 | n/a | n/a | n/a |  |  | full |
| Substitute Algorithm: clear_refactor_pending.py writes the ledger through `ledger.replace_ledger` and its backup / in-place rewrite / restore fallback (`write_beside`, `holds`, `open(argv[0], "wb")`) is deleted, its behaviour on a symlinked ledger and on a failed write unchanged — predicate, run from skills/tdd/scripts: `grep -F 'ledger.replace_ledger(' veri/clear_refactor_pending.py >/dev/null && ! grep -E 'write_beside|def holds|backup|"wb"' veri/clear_refactor_pending.py >/dev/null` ⟦criterion 1⟧ | 5 | 1 | 0 | 0 | 0 | 0 | 187 | 40 | 78 | 17394 | 2083330 | 268190 | 2.67 | 200 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 11 | 11 | 62 | 4 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 61 | 120 | 26178 | 3067480 | 449094 | 4.08 |
