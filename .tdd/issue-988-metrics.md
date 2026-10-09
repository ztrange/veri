### 📊 Metrics — issue 988

Wall time for the issue: 634 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: unknown of 2 planned.
Outcome: the run bailed — uncovered, a process failure.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 15 | 4 | 8 | 1752 | 156525 | 38816 | 0.20 |
| cover | 1 | 0 | 0 | 0 | 572 | 58 | 15 | 30 | 4677 | 728127 | 43060 | 0.58 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 1 | 1 | 0 | 0 | 20 | 15 | 4 | 8 | 1752 | 156525 | 38816 | 0.20 |
| developer | claude-opus-5-5 | 1 | 0 | 0 | 0 | 572 | 58 | 15 | 30 | 4677 | 728127 | 43060 | 0.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 572 | 0.58 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract the exit-status contract phrase into one partial: the words "The wrapper hands the command's own exit status straight back," move into a new `skills/tdd/scripts/prompts/_exit-status-back.md`, and each of the 12 templates (develop-green, develop-rebase, develop-reconcile, develop-red, develop-refactor, develop-revise, verify-diff, verify-green, verify-pin, verify-rebase, verify-red, verify-refactor) includes it with `{{INCLUDE:_exit-status-back.md}}` in place of spelling it, each keeping its own continuation, so every built prompt's text is byte-identical. Predicate, false before and true after: `p=skills/tdd/scripts/prompts; [ "$(grep -l 'exit status straight back' $p/*.md | wc -l | tr -d ' ')" = 1 ] && [ -f $p/_exit-status-back.md ] && grep -q 'exit status straight back' $p/_exit-status-back.md && [ "$(grep -l '{{INCLUDE:_exit-status-back.md}}' $p/develop-green.md $p/develop-rebase.md $p/develop-reconcile.md $p/develop-red.md $p/develop-refactor.md $p/develop-revise.md $p/verify-diff.md $p/verify-green.md $p/verify-pin.md $p/verify-rebase.md $p/verify-red.md $p/verify-refactor.md | wc -l | tr -d ' ')" = 12 ]` ⟦criterion 1⟧ | 1 | 0 | 0 | 0 | 0 | 0 | 58 | 15 | 30 | 4677 | 728127 | 43060 | 0.58 | unknown | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s |
| --- | ---: | ---: | ---: | ---: |
| affected | 6 | 2 | 39 | 463 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 19 | 38 | 6429 | 884652 | 81876 | 0.79 |
