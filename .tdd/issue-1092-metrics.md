### 📊 Metrics — issue 1092

Wall time for the issue: 421 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 1 of 2 planned.
Outcome: the run bailed — uncovered, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 2 | 4 | 1239 | 66047 | 43921 | 0.19 |
| cover | 2 | 0 | 0 | 0 | 57 | 42 | 11 | 22 | 4265 | 516618 | 91362 | 0.92 |
| transform | 3 | 1 | 0 | 0 | 210 | 108 | 24 | 46 | 10399 | 1234945 | 165179 | 1.56 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 2 | 2 | 0 | 0 | 96 | 25 | 7 | 14 | 2808 | 289222 | 87592 | 0.41 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 186 | 136 | 30 | 58 | 13095 | 1528388 | 212870 | 2.27 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 30 | 0.48 |
| transform | 0 | 0.00 | 59 | 0.79 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Function: move tick_ledger.py's temp-file-beside-the-real-path-then-os.replace write into one helper `replace_ledger(path, data)` in veri/ledger.py and have tick_ledger.py call it, its behaviour on a symlinked ledger and on a failed write unchanged — predicate, run from skills/tdd/scripts: `grep -F 'def replace_ledger(' veri/ledger.py >/dev/null && grep -F 'ledger.replace_ledger(' veri/tick_ledger.py >/dev/null && ! grep -F 'mkstemp' veri/tick_ledger.py >/dev/null` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 75 | 19 | 38 | 7545 | 918103 | 136983 | 1.22 | 236 | n/a | n/a | n/a |  |  | full |
| Substitute Algorithm: clear_refactor_pending.py writes the ledger through `ledger.replace_ledger` and its backup / in-place rewrite / restore fallback (`write_beside`, `holds`, `open(argv[0], "wb")`) is deleted, its behaviour on a symlinked ledger and on a failed write unchanged — predicate, run from skills/tdd/scripts: `grep -F 'ledger.replace_ledger(' veri/clear_refactor_pending.py >/dev/null && ! grep -E 'write_beside|def holds|backup|"wb"' veri/clear_refactor_pending.py >/dev/null` ⟦criterion 1⟧ | 2 | 0 | 0 | 0 | 0 | 0 | 75 | 16 | 30 | 7119 | 833460 | 119558 | 1.27 | unknown | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s |
| --- | ---: | ---: | ---: |
| affected | 11 | 11 | 62 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 37 | 72 | 15903 | 1817610 | 300462 | 2.68 |
