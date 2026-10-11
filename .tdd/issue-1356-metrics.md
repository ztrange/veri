### 📊 Metrics — issue 1356

Wall time for the issue: 3007 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1489.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER sonnet, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 7 | 2 | 4 | 1004 | 57937 | 39839 | 0.18 |
| diff | 4 | 2 | 0 | 0 | 994 | 195 | 44 | 86 | 24557 | 2953555 | 234649 | 1.48 |
| expand | 2 | 1 | 0 | 0 | 112 | 37 | 13 | 24 | 4459 | 554855 | 88886 | 0.46 |
| migrate | 2 | 1 | 0 | 0 | 235 | 48 | 19 | 38 | 5838 | 941475 | 89521 | 0.51 |
| contract-a | 2 | 1 | 0 | 0 | 677 | 36 | 13 | 26 | 4151 | 627599 | 98464 | 0.50 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 6 | 6 | 0 | 0 | 722 | 104 | 33 | 64 | 12139 | 1419202 | 267372 | 1.33 |
| developer | claude-sonnet-5-5 | 5 | 0 | 0 | 0 | 1307 | 219 | 58 | 114 | 27870 | 3716219 | 283987 | 1.79 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| expand | 0 | 0.00 | 112 | 0.46 |
| migrate | 0 | 0.00 | 235 | 0.51 |
| contract-a | 0 | 0.00 | 677 | 0.50 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Before any production change, every tests/py/test_verify.py case that answers build-verify-prompt.sh through a faked process or asserts its argv asserts the prompt instead — the bytes in .tdd/verify-<phase>.prompt, rendered by the real builder from a spec file and test path written in the case's own scratch tree — with a refusal driven by an input the builder refuses (a missing spec file) rather than a faked exit, no case in that file answering or asserting build-verify-prompt.sh by name, green against today's code, in a commit that changes only paths under skills/tdd/scripts/tests/ ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 151 | 29 | 58 | 20140 | 2299055 | 140119 | 0.99 | 583 | n/a | n/a | n/a |  |  | full |
| verify gives its full answer — exit code, stdout, stderr, and the .tdd/verify-<phase>.prompt file and events — when starting build-verify-prompt.sh as a process would fail, in a case that refuses that start at the process boundary, calling a function veri/build_verify_prompt.py exposes that returns the exit code and the prompt text and takes only what verify passes the builder today (the --step and --fast-cmd values, the phase, spec, test path and test id or base sha), no rationale parameter ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 13 | 24 | 4459 | 554855 | 88886 | 0.46 | unknown | unknown | unknown | unknown |  |  | full |
| verify gives its full answer — exit code, stdout, stderr, and the .tdd/verify-<phase>.prompt file and events — when starting build-verify-prompt.sh as a process would fail, in a case that refuses that start at the process boundary, calling a function veri/build_verify_prompt.py exposes that returns the exit code and the prompt text and takes only what verify passes the builder today (the --step and --fast-cmd values, the phase, spec, test path and test id or base sha), no rationale parameter ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 19 | 38 | 5838 | 941475 | 89521 | 0.51 | unknown | unknown | unknown | unknown |  |  | full |
| verify gives its full answer — exit code, stdout, stderr, and the .tdd/verify-<phase>.prompt file and events — when starting build-verify-prompt.sh as a process would fail, in a case that refuses that start at the process boundary, calling a function veri/build_verify_prompt.py exposes that returns the exit code and the prompt text and takes only what verify passes the builder today (the --step and --fast-cmd values, the phase, spec, test path and test id or base sha), no rationale parameter ⟦phases: expand, migrate, contract-a⟧ ⟦criterion 2⟧ ⟂ expand done ⟂ migrate done | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 13 | 26 | 4151 | 627599 | 98464 | 0.50 | unknown | unknown | unknown | unknown |  |  | full |
| No test of verify fakes build-verify-prompt.sh at the process boundary any longer: each such test is rewritten against the function or deleted under ADR 0030's mutation parity, in a commit that changes no production file ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 15 | 28 | 4417 | 654500 | 94530 | 0.49 | 464 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 24 | 27 | 24 | 25 | 26 |  |  |  |  |  |  |  |  |  |  |
| affected | 290 | 26 | 2 | 2 | 1 | 9 | 11 | 14 | 0 | 68 | 24 | 289 | 297 | 25 | 297 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 91 | 178 | 40009 | 5135421 | 551359 | 3.12 |
