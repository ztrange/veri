### 📊 Metrics — issue 1396

Wall time for the issue: 2433 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1403.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 19 | 14 | 2 | 4 | 1464 | 66114 | 42944 | 0.19 |
| red | 2 | 0 | 0 | 0 | 99 | 82 | 19 | 34 | 8611 | 922965 | 103670 | 1.19 |
| pin | 2 | 2 | 0 | 0 | 49 | 32 | 9 | 18 | 3721 | 405653 | 89470 | 0.44 |
| diff | 2 | 1 | 0 | 0 | 203 | 75 | 21 | 42 | 7178 | 1175248 | 106198 | 0.97 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 4 | 4 | 0 | 0 | 157 | 72 | 18 | 36 | 7957 | 824889 | 182170 | 0.89 |
| developer | claude-opus-5-5 | 3 | 0 | 0 | 0 | 213 | 131 | 33 | 62 | 13017 | 1745091 | 160112 | 1.89 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When a real file-size limit (`RLIMIT_FSIZE`, with `SIGXFSZ` ignored) makes writing the cleared ledger fail, `clear-refactor-pending.sh` exits 2, a symlinked ledger stays a symlink, the file it points at is byte-identical to before, and no file is left beside the link or its target — forced at the size limit only, never by faking a call of today's backup-and-rewrite writer ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 63 | 14 | 26 | 6738 | 668299 | 97179 | 0.83 | unknown | unknown | unknown | unknown |  |  | pin |
| When `tempfile.mkstemp` fails while the cleared ledger is being written, `clear-refactor-pending.sh` exits 2, the ledger is byte-identical to before and no file is left beside it — forced by failing `tempfile.mkstemp` only, never by faking `builtins.open`, `os.open`, `os.replace` or `os.unlink` ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 14 | 26 | 5594 | 660319 | 95961 | 0.79 | unknown | unknown | unknown | unknown |  |  | pin |
| The ten mechanism-coupled cases named in the issue's first comment (lines 227, 246, 325, 369, 473, 552, 607, 661, 699, 743 of `skills/tdd/scripts/tests/py/test_clear_refactor_pending.py`) are each deleted or rewritten so that it forces the failure at the size-limit or `tempfile.mkstemp` seam only; no other case in the file changes ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 75 | 21 | 42 | 7178 | 1175248 | 106198 | 0.97 | 228 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 0 | 1 |  |  |  |
| target | 2 | 1 | 0 | 0 | 1 | 1 |
| fast | 57 | 57 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 51 | 98 | 20974 | 2569980 | 342282 | 2.78 |
