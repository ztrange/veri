### 📊 Metrics — issue 743

Wall time for the issue: 4378 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/893.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 30 | 24 | 3 | 6 | 2661 | 119242 | 46325 | 0.45 |
| cover | 3 | 0 | 0 | 0 | 121 | 45 | 13 | 26 | 4288 | 573738 | 128755 | 1.23 |
| transform | 7 | 3 | 0 | 0 | 1900 | 210 | 46 | 90 | 19083 | 2210596 | 284865 | 3.10 |
| diff | 2 | 1 | 0 | 0 | 96 | 23 | 5 | 10 | 1514 | 174161 | 77768 | 0.69 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 6 | 5 | 0 | 0 | 1097 | 114 | 27 | 54 | 12288 | 1225032 | 225791 | 2.30 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 1050 | 188 | 40 | 78 | 15258 | 1852705 | 311922 | 3.17 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Function: add `ledger_first_step <predicate>` to `skills/tdd/scripts/lib/ledger.sh` — it reads records by calling `ledger_steps` by name, runs `ledger_fields` on each, calls the caller-named predicate, prints the first matching record's `text` and returns 0, else prints nothing and returns 3 — and replace `next-unchecked.sh`'s own loop over `ledger_steps` with a call to it, its predicate an open `step` or `diff-checked` step. Predicate, false before and true after: `grep -Eq '^ledger_first_step\(\)' skills/tdd/scripts/lib/ledger.sh && ! grep -Fq '< <(ledger_steps)' skills/tdd/scripts/next-unchecked.sh && grep -Fq 'ledger_first_step' skills/tdd/scripts/next-unchecked.sh` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 60 | 14 | 28 | 6309 | 615953 | 131338 | 1.30 | 241 | unknown | unknown | unknown |  |  | full |
| Replace Loop with Function Call: `next-pending-refactor.sh` drops its own loop over `ledger_steps` and calls `ledger_first_step` with a predicate for a done step whose `pending` is 1. Predicate, false before and true after: `! grep -Fq '< <(ledger_steps)' skills/tdd/scripts/next-pending-refactor.sh && grep -Fq 'ledger_first_step' skills/tdd/scripts/next-pending-refactor.sh` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 66 | 19 | 36 | 6614 | 829439 | 127217 | 1.32 | 181 | unknown | unknown | unknown |  |  | full |
| Introduce Explaining Variable on the eleven `SKILL.md` lines that write a `step-added`, `step-split` or `step-escalated` mark: each reads its ledger answer once into a shell variable on the same line and uses it for both `VERI_STEP=` and `anchor=`, as one command in one Bash call. `skill-criterion-finished.test.sh:268` still needs some line with the literal `event.sh step-added anchor="$(` that also names `ledger-steps.sh`, so the two `ledger-steps.sh last-done` step-added lines keep `anchor="$(` around the variable rather than a second ledger read. Predicate, false before and true after: `[ "$(grep -E 'event\.sh (step-added|step-split|step-escalated)' skills/tdd/SKILL.md | grep -c 'issue-<n>\.md.*issue-<n>\.md')" = 0 ] && [ "$(grep -cE 'event\.sh (step-added|step-split|step-escalated)' skills/tdd/SKILL.md)" -ge 12 ]` ⟦criterion 2⟧ | 4 | 1 | 0 | 0 | 0 | 1 | 129 | 26 | 52 | 10448 | 1338942 | 155065 | 1.72 | 1718 | unknown | unknown | unknown |  |  | full |
| no test file is changed anywhere on the branch ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 5 | 10 | 1514 | 174161 | 77768 | 0.69 | 117 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 98 | 15 | 0 | 51 | 0 | 1 | 2 | 10 | 56 | 51 | 496 | 138 | 59 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 67 | 132 | 27546 | 3077737 | 537713 | 5.47 |
