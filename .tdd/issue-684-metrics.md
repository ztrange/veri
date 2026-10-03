### 📊 Metrics — issue 684

Wall time for the issue: 3740 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 5 of 9 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/738.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 22 | 17 | 2 | 4 | 1785 | 61249 | 39803 | 0.37 |
| cover | 7 | 0 | 0 | 0 | 185 | 114 | 31 | 62 | 11317 | 1298199 | 282283 | 2.74 |
| transform | 13 | 6 | 0 | 0 | 834 | 370 | 86 | 168 | 33172 | 3876196 | 556644 | 5.89 |
| rebase | 2 | 1 | 0 | 0 | 1561 | 77 | 11 | 24 | 4231 | 598481 | 56149 | 1.13 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 8 | 8 | 0 | 0 | 1121 | 203 | 43 | 84 | 16922 | 1862749 | 339563 | 3.43 |
| developer | claude-opus-5-5 | 15 | 0 | 0 | 0 | 1481 | 375 | 87 | 174 | 33583 | 3971376 | 595316 | 6.71 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 34 | 0.43 |
| transform | 0 | 0.00 | 192 | 0.90 |
| rebase | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Move the record split into lib/ledger.sh: add a `ledger_fields <record>` function there that hands its caller a `ledger_steps` record's fields by name (index, state, kind, pending, added, criterion, text), and make criterion-finished.sh read its fields through it instead of `mapfile -td`. Predicate: `grep -qE '^ledger_fields\(\)' skills/tdd/scripts/lib/ledger.sh && grep -qF ledger_fields skills/tdd/scripts/criterion-finished.sh && ! grep -qF 'mapfile -td' skills/tdd/scripts/criterion-finished.sh` ⟦criterion 2⟧ | 5 | 1 | 0 | 0 | 0 | 0 | 145 | 33 | 62 | 14006 | 1443215 | 216673 | 2.30 | 211 | unknown | unknown | unknown |  |  | full |
| next-unchecked.sh picks the first open `step`-kind record through `ledger_fields` instead of its positional regex. Predicate: `grep -qF ledger_fields skills/tdd/scripts/next-unchecked.sh && ! grep -qF '[^\t]' skills/tdd/scripts/next-unchecked.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 70 | 18 | 36 | 5884 | 808981 | 123512 | 1.27 | 160 | unknown | unknown | unknown |  |  | full |
| next-pending-refactor.sh picks the first done, refactor-pending record through `ledger_fields` instead of its positional regex. Predicate: `grep -qF ledger_fields skills/tdd/scripts/next-pending-refactor.sh && ! grep -qF '[^\t]' skills/tdd/scripts/next-pending-refactor.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 53 | 16 | 32 | 5012 | 703402 | 122309 | 1.22 | 100 | unknown | unknown | unknown |  |  | full |
| preserve-attempt.sh's `ledger_step_index` reads a record's index and text through `ledger_fields` instead of `"$tab"*` globs. Predicate: `grep -qF ledger_fields skills/tdd/scripts/preserve-attempt.sh && ! grep -qF '"$tab"*"$tab"' skills/tdd/scripts/preserve-attempt.sh` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 61 | 16 | 32 | 6437 | 699158 | 124183 | 1.26 | 172 | unknown | unknown | unknown |  |  | full |
| add-ledger-step.sh reads the `⟦added⟧` mark and the `⟦criterion ` tag from lib/ledger.sh (`_ledger_added_mark`, `_ledger_criterion_tag`) instead of spelling them. Predicate: `! grep -v '^#' skills/tdd/scripts/add-ledger-step.sh | grep -nF -e '⟦added⟧' -e '⟦criterion '` ⟦criterion 3⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 132 | 27 | 56 | 9980 | 1303306 | 181683 | 2.39 | 2013 | unknown | unknown | unknown |  |  | full |
| ledger-steps.sh's readers (current, last-done, criterion) pick records through `ledger_fields` instead of positional regexes — the fifth positional split, added on main by #682 after the issue was written. Predicate: `grep -qF ledger_fields skills/tdd/scripts/ledger-steps.sh && ! grep -qF '[^\t]' skills/tdd/scripts/ledger-steps.sh` ⟦added⟧ ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 100 | 18 | 36 | 7401 | 814814 | 126716 | 1.32 | unknown | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 27 | 32 | 1 | 33 | 9 | 24 | 0 | 1 | 32 | 7 | 0 | 0 | 5 | 4 | 6 | 5 | 5 | 6 | 6 | 7 | 6 | 3 | 2 | 8 | 2 | 2 | 1 | 0 | 0 | 1 | 61 | 17 | 1 |
| all | 739 | 741 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 130 | 258 | 50505 | 5834125 | 934879 | 10.14 |
