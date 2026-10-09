### 📊 Metrics — issue 988

Wall time for the issue: 1171 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 2 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1256.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 20 | 15 | 4 | 8 | 1752 | 156525 | 38816 | 0.20 |
| cover | 4 | 0 | 0 | 0 | 1120 | 152 | 37 | 74 | 12886 | 1699907 | 166368 | 1.93 |
| transform | 5 | 2 | 0 | 0 | 301 | 185 | 47 | 94 | 17614 | 2217475 | 214512 | 2.14 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 109 | 55 | 17 | 34 | 5775 | 733084 | 121358 | 0.69 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 1332 | 297 | 71 | 142 | 26477 | 3340823 | 298338 | 3.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract the exit-status contract phrase into one partial: the words "The wrapper hands the command's own exit status straight back," move into a new `skills/tdd/scripts/prompts/_exit-status-back.md`, and each of the 12 templates (develop-green, develop-rebase, develop-reconcile, develop-red, develop-refactor, develop-revise, verify-diff, verify-green, verify-pin, verify-rebase, verify-red, verify-refactor) includes it with `{{INCLUDE:_exit-status-back.md}}` in place of spelling it, each keeping its own continuation, so every built prompt's text is byte-identical. Predicate, false before and true after: `p=skills/tdd/scripts/prompts; [ "$(grep -l 'exit status straight back' $p/*.md | wc -l | tr -d ' ')" = 1 ] && [ -f $p/_exit-status-back.md ] && grep -q 'exit status straight back' $p/_exit-status-back.md && [ "$(grep -l '{{INCLUDE:_exit-status-back.md}}' $p/develop-green.md $p/develop-rebase.md $p/develop-reconcile.md $p/develop-red.md $p/develop-refactor.md $p/develop-revise.md $p/verify-diff.md $p/verify-green.md $p/verify-pin.md $p/verify-rebase.md $p/verify-red.md $p/verify-refactor.md | wc -l | tr -d ' ')" = 12 ]` ⟦criterion 1⟧ | 4 | 1 | 0 | 0 | 0 | 0 | 151 | 41 | 82 | 12954 | 1921163 | 169045 | 1.81 | 623 | n/a | n/a | n/a |  |  | full |
| Extract the shared safety block into one partial: the 18 lines `_shared.md:22-39` and `_develop-shared.md:23-40` both spell byte for byte (the `git stash` rule with its `{{INCLUDE:_probe-restore.md}}`, the global-configuration rule, and `{{INCLUDE:_signal-own-processes.md}}`) move into a new `skills/tdd/scripts/prompts/_leaf-safety.md`, which both files include with `{{INCLUDE:_leaf-safety.md}}`, so every built prompt's text is byte-identical. Predicate, false before and true after: `p=skills/tdd/scripts/prompts; [ "$(grep -l 'Never run `git stash`' $p/*.md | tr '\n' ' ')" = "$p/_leaf-safety.md " ] && [ "$(grep -l 'Never change global or user-level configuration' $p/*.md | tr '\n' ' ')" = "$p/_leaf-safety.md " ] && grep -q '{{INCLUDE:_leaf-safety.md}}' $p/_shared.md && grep -q '{{INCLUDE:_leaf-safety.md}}' $p/_develop-shared.md` ⟦criterion 2⟧ | 5 | 1 | 0 | 0 | 0 | 0 | 186 | 43 | 86 | 17546 | 1996219 | 211835 | 2.26 | 259 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 6 | 2 | 39 | 463 | 432 | 6 | 2 | 1 | 0 | 2 | 1 | 2 | 1 | 43 | 30 | 0 | 0 | 0 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 88 | 176 | 32252 | 4073907 | 419696 | 4.27 |
