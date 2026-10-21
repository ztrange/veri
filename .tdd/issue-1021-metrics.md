### 📊 Metrics — issue 1021

Wall time for the issue: 3340 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 14 of 14 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1944.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE opus; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 42 | 37 | 11 | 22 | 4506 | 339221 | 36184 | 0.17 |
| red | 10 | 1 | 0 | 0 | 303 | 253 | 80 | 160 | 31503 | 2752759 | 228901 | 1.16 |
| pin | 8 | 8 | 0 | 0 | 132 | 95 | 33 | 66 | 9883 | 889937 | 113944 | 0.47 |
| green | 2 | 1 | 0 | 0 | 46 | 20 | 9 | 18 | 2022 | 249373 | 27653 | 0.11 |
| refactor | 2 | 1 | 0 | 0 | 36 | 23 | 9 | 18 | 2088 | 257557 | 30329 | 0.12 |
| diff | 10 | 5 | 0 | 0 | 1740 | 230 | 90 | 174 | 23906 | 2799881 | 194825 | 1.01 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 18 | 17 | 1 | 0 | 1219 | 261 | 90 | 180 | 26024 | 2547288 | 275613 | 1.20 |
| developer | claude-sonnet-5-5 | 16 | 0 | 0 | 0 | 1080 | 397 | 142 | 278 | 47884 | 4741440 | 356223 | 1.84 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| `ledger-steps.sh` and `next-unchecked.sh` treat an unchecked line `- [ ] <criterion>: repairs the fixture '<name>' in <fixture file>, reproduced by a case in <test file> ⟦fixture-repair⟧ ⟦criterion k⟧` as an ordinary step: `ledger-steps.sh` prints it with kind `step` and its criterion k, and `next-unchecked.sh` hands it over ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 15 | 30 | 4780 | 485293 | 38222 | 0.19 | unknown | unknown | unknown | unknown |  |  | pin |
| `tests-frozen.sh record --step` on a step whose trailing marks carry `⟦fixture-repair⟧` writes no record file, and `check --step` on it exits 0 even with a test file changed, exactly as for the `⟦suite-repair⟧` and `⟦ci-repair⟧` marks; an unmarked step is still frozen ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 79 | 29 | 58 | 8556 | 836882 | 92510 | 0.40 | 221 | unknown | 1/5 | nothing-structural |  |  | full |
| SKILL.md's Scope & plan section gains text naming the `⟦fixture-repair⟧` mark and its line shape (`- [ ] <criterion>: repairs the fixture '<fixture or stub name>' in <fixture file>, reproduced by a case in <test file> ⟦fixture-repair⟧ ⟦criterion k⟧`), saying it is used only for a defect in a test's fixture, stub or harness whose script under test is correct, that the fixture is named by a function, stub or helper rather than a line range, that `<fixture file>` must be a test file by `transform-touches-tests.sh`'s rule, and that such a step is an ordinary Red/Green step whose criterion is that the reproducing case passes against the unchanged script under test — the exception to routing a change satisfiable only by editing a test to `⟦diff-checked⟧` or the pin; the text and every checksum or verbatim pin it moves land in one commit ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 19 | 36 | 5088 | 555559 | 33971 | 0.19 | 624 | n/a | n/a | n/a |  |  | full |
| A prose case reading SKILL.md's Scope & plan section pins the `⟦fixture-repair⟧` text: it goes red when the mark's line shape, the fixture/stub/harness-only condition, or the test-file rule for `<fixture file>` is removed ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 30 | 10 | 20 | 3873 | 297988 | 33516 | 0.15 | unknown | unknown | unknown | unknown |  |  | pin |
| `prompts/verify-plan.md` gains text naming the `⟦fixture-repair⟧` mark and its line shape, accepting a well-formed `⟦fixture-repair⟧` step as the exception to rejecting a test-only change planned as Red/Green, and telling the plan verifier to REJECT a `⟦fixture-repair⟧` step whose spec places the defect in the script under test, one that names no fixture, and one whose fixture file is not a test file by `transform-touches-tests.sh`'s rule; the text and every checksum or verbatim pin it moves land in one commit ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 47 | 19 | 38 | 4760 | 612142 | 37228 | 0.20 | 260 | n/a | n/a | n/a |  |  | full |
| A case on the plan prompt `build-verify-prompt.sh plan` renders pins the `⟦fixture-repair⟧` text: it goes red when any of the three REJECT conditions (defect in the script under test, no fixture named, fixture file not a test file) or the mark's line shape is removed ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 16 | 32 | 5502 | 536949 | 39737 | 0.21 | unknown | unknown | unknown | unknown |  |  | pin |
| `build-develop-prompt.sh` gains a `{{FIXTURE_REPAIR}}` slot in `develop-green.md`'s failing-test section and a fixture-repair partial in `prompts/`, filled in phase `green` and in phase `revise` redoing `green` for a step whose trailing marks carry `⟦fixture-repair⟧`, with a paragraph permitting edits to the fixture the step names and to nothing else — not the target case, not any other case, not any production file; an unmarked step and every other phase render byte-identical to today; the text, the wiring and every checksum or verbatim pin they move land in one commit ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 48 | 19 | 36 | 5555 | 603175 | 43012 | 0.22 | 264 | n/a | n/a | n/a |  |  | full |
| A case pins `build-develop-prompt.sh`'s fixture-repair paragraph: present in green and revise-green prompts for a `⟦fixture-repair⟧` step, saying edits are permitted to the named fixture only and not to the target case, any other case or any production file, and absent from an unmarked step's green prompt and from a marked step's red and refactor prompts ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 38 | 13 | 26 | 5095 | 430714 | 40470 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| A case pins that `build-develop-prompt.sh` green for a `⟦fixture-repair⟧` step exits 2 with a stderr line naming the fixture-repair partial's path when that partial file is missing ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 46 | 13 | 26 | 4855 | 459093 | 41233 | 0.20 | unknown | unknown | unknown | unknown |  |  | pin |
| `build-verify-prompt.sh` gains a `{{FIXTURE_REPAIR}}` slot in `verify-green.md`'s genuine-pass check and a fixture-repair partial in `prompts/`, filled in phase `green` for a step whose trailing marks carry `⟦fixture-repair⟧`, with a paragraph telling the verifier to REJECT, naming the path or hunk, any change outside the target test's file, the named fixture file and Red's case, and to PASS only when the target case passes with every change confined to those; an unmarked step and every other phase render byte-identical to today; the text, the wiring and every checksum or verbatim pin they move land in one commit ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 37 | 15 | 30 | 3535 | 477632 | 38548 | 0.18 | 249 | n/a | n/a | n/a |  |  | full |
| A case pins `build-verify-prompt.sh`'s fixture-repair paragraph: present in the green prompt for a `⟦fixture-repair⟧` step with its REJECT-naming-path-or-hunk and PASS-only-when-confined rules, absent from an unmarked step's green prompt and from a marked step's red and refactor prompts ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 36 | 11 | 22 | 4180 | 350838 | 40561 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| A case pins that `build-verify-prompt.sh` green for a `⟦fixture-repair⟧` step exits 2 with a stderr line naming the fixture-repair partial's path when that partial file is missing ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 41 | 13 | 26 | 4483 | 411554 | 38269 | 0.18 | unknown | unknown | unknown | unknown |  |  | pin |
| SKILL.md gains text saying a `⟦fixture-repair⟧` step's verify-green PASS is ticked with `tick-ledger.sh` without `--refactor-pending`, committed with a `test:` subject, runs no refactor loop, and ticks its issue criterion with `tick-issue-criterion.sh` on `criterion-finished.sh` exit 0 (ticking nothing on exit 3), as a `⟦diff-checked⟧` PASS does; the text and every checksum or verbatim pin it moves land in one commit ⟦diff-checked⟧ ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 54 | 18 | 34 | 4968 | 551373 | 42066 | 0.21 | 444 | n/a | n/a | n/a |  |  | full |
| A prose case reading SKILL.md pins the `⟦fixture-repair⟧` PASS handling: it goes red when the sentence is removed, when it says `--refactor-pending`, or when it names a subject other than `test:` ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 33 | 11 | 22 | 4172 | 340315 | 36309 | 0.17 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `tests-frozen.sh record --step` on a step whose trailing marks carry `⟦fixture-repair⟧` writes no record file, and `check --step` on it exits 0 even with a test file changed, exactly as for the `⟦suite-repair⟧` and `⟦ci-repair⟧` marks; an unmarked step is still frozen ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 36 | 0.12 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 1 | 1 | 1 | 0 | 0 | 4 | 0 | 1 | 0 | 171 | 170 | 0 | 3 | 1 | 2 | 1 | 0 | 4 | 0 | 169 | 2 | 2 | 3 | 2 | 1 | 165 |
| target | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 1 | 1 | 6 | 0 | 1 | 1 | 1 | 0 |  |  |  |  |  |  |  |  |  |  |
| fast | 6 | 7 | 6 | 6 | 7 | 6 | 6 | 8 | 6 | 6 | 5 | 6 | 7 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 232 | 458 | 73908 | 7288728 | 631836 | 3.05 |
