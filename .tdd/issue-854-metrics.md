### 📊 Metrics — issue 854

Wall time for the issue: 931 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 2 of 6 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/953.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 10 | 8 | 1 | 2 | 1021 | 11731 | 34075 | 0.15 |
| cover | 2 | 0 | 0 | 0 | 33 | 27 | 6 | 12 | 2088 | 213578 | 77901 | 0.71 |
| transform | 4 | 2 | 0 | 0 | 103 | 73 | 18 | 36 | 7253 | 738760 | 159665 | 1.24 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 3 | 3 | 0 | 0 | 47 | 28 | 7 | 14 | 3281 | 220978 | 110808 | 0.52 |
| developer | claude-opus-5-5 | 4 | 0 | 0 | 0 | 99 | 80 | 18 | 36 | 7081 | 743091 | 160833 | 1.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Function into `skills/tdd/scripts/lib/detach.sh`: the `python3 -c 'import os, signal, sys; signal.signal(signal.SIGPIPE, signal.SIG_DFL); os.setsid(); os.execvp(sys.argv[1], sys.argv[1:])'` launcher moves out of `detach-leaf.sh` into one function in the new lib, which `exec`s it, and `detach-leaf.sh` sources the lib and calls that function with `&` after its unchanged usage check; its `USAGE`, `refuse` and `exit-contract.sh` source line stay. Predicate: `grep -q SIG_DFL skills/tdd/scripts/lib/detach.sh && ! grep -q SIG_DFL skills/tdd/scripts/detach-leaf.sh && grep -q 'lib/detach.sh' skills/tdd/scripts/detach-leaf.sh` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 55 | 13 | 26 | 5318 | 526994 | 118395 | 0.99 | 113 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call: `detach-command.sh start` sources `skills/tdd/scripts/lib/detach.sh` and launches its `sh -c '…' "$exit_file" "$@"` wrapper through the lib's function, output to `.tdd/<name>.out`, stdin from `/dev/null`, backgrounded with `&` and `$!` written to `.tdd/<name>.pid` as before; its `start`/`wait` logic, `USAGE` and `refuse` calls stay. Predicate: `! grep -q SIG_DFL skills/tdd/scripts/detach-command.sh && grep -q 'lib/detach.sh' skills/tdd/scripts/detach-command.sh && [ "$(grep -rl SIG_DFL skills/tdd/scripts --include='*.sh')" = skills/tdd/scripts/lib/detach.sh ]` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 45 | 11 | 22 | 4023 | 425344 | 119171 | 0.96 | 95 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s |
| --- | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 4 | 0 | 3 | 7 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 25 | 50 | 10362 | 964069 | 271641 | 2.10 |
