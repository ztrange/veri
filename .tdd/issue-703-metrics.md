### 📊 Metrics — issue 703

Wall time for the issue: 3942 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/895.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 17 | 14 | 1 | 2 | 1812 | 11866 | 31649 | 0.15 |
| red | 12 | 5 | 0 | 0 | 519 | 412 | 96 | 188 | 34863 | 4497827 | 516207 | 4.91 |
| green | 10 | 5 | 0 | 0 | 580 | 277 | 72 | 140 | 25500 | 3104342 | 402925 | 3.46 |
| refactor | 10 | 5 | 0 | 0 | 349 | 213 | 60 | 118 | 19280 | 2588356 | 402123 | 3.27 |
| pin | 2 | 2 | 0 | 0 | 51 | 33 | 10 | 20 | 3188 | 402499 | 77120 | 0.42 |
| diff | 9 | 4 | 0 | 0 | 889 | 720 | 98 | 194 | 70300 | 6285547 | 491761 | 5.65 |
| predicate | 1 | 0 | 0 | 0 | 14 | 11 | 3 | 6 | 812 | 104615 | 38351 | 0.34 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 22 | 22 | 0 | 0 | 851 | 446 | 127 | 250 | 47622 | 5410853 | 877100 | 5.07 |
| developer | claude-opus-5-5 | 23 | 0 | 0 | 0 | 1568 | 1234 | 213 | 418 | 108133 | 11584199 | 1083036 | 13.15 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| predicate | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| build-develop-prompt.sh replaces a `{{INCLUDE:<file>}}` token in a template with the contents of `skills/tdd/scripts/prompts/<file>` (trailing newlines stripped, as `$(cat …)` does), before every other substitution, so a placeholder inside the partial is still filled | 6 | 3 | 0 | 0 | 0 | 0 | 132 | 37 | 68 | 11374 | 1527874 | 246543 | 2.01 | 367 | unknown | 0/5 | structural-owed |  |  | full |
| build-develop-prompt.sh resolves a `{{INCLUDE:<file>}}` token that appears inside an included partial, recursively | 6 | 3 | 0 | 0 | 0 | 0 | 125 | 36 | 72 | 10651 | 1533670 | 234472 | 1.90 | 223 | unknown | 0/5 | nothing-left |  |  | full |
| build-verify-prompt.sh replaces a `{{INCLUDE:<file>}}` token in a template, and inside an included partial recursively, with that partial's contents before every other substitution, taking no new parameter ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 181 | 44 | 86 | 16686 | 2000136 | 255481 | 2.25 | 297 | unknown | 1/5 | nothing-left |  |  | full |
| a template or partial whose `{{INCLUDE:<file>}}` names a partial that does not exist makes build-develop-prompt.sh exit 2 with the missing file's path on stderr and nothing on stdout ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 178 | 48 | 94 | 16929 | 2187741 | 249497 | 2.25 | 298 | unknown | 1/5 | nothing-left |  |  | full |
| a template or partial whose `{{INCLUDE:<file>}}` names a partial that does not exist makes build-verify-prompt.sh exit 2 with the missing file's path on stderr and nothing on stdout ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 65 | 16 | 32 | 5830 | 760571 | 83564 | 0.78 | unknown | unknown | unknown | unknown |  |  | pin |
| a partial that includes itself, directly or through another partial, makes build-develop-prompt.sh exit 2 naming the file on stderr, with nothing on stdout, rather than looping ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 179 | 40 | 80 | 15455 | 1791728 | 245119 | 2.11 | 335 | unknown | 0/5 | nothing-left |  |  | full |
| a partial that includes itself, directly or through another partial, makes build-verify-prompt.sh exit 2 naming the file on stderr, with nothing on stdout, rather than looping ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 75 | 17 | 34 | 5906 | 791304 | 83699 | 0.77 | unknown | unknown | unknown | unknown |  |  | pin |
| the develop-only passages of the issue's table — the `SPLIT:` "When the step is too big for one green" section, the three "fresh leaf" openings, the spec + test-command sections of develop-over-budget.md and develop-exhausted.md, the "every `[x]` tick and every ` ⟂ refactor pending` mark must survive" sentence, the "structural pass" sentence, and the lines develop-structural.md shares with develop-transform.md — each live in exactly one file under prompts/, every other template reaching it through `{{INCLUDE:…}}`, with any wording that differed between copies left in the template that needs it, and every rendered prompt byte-identical to the merge base's ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 239 | 24 | 48 | 23312 | 1557034 | 138101 | 1.60 | 283 | unknown | unknown | unknown |  |  | full |
| the remaining passages of the issue's table — the `run-suite.sh <suite>` sentence, the `{{TIMED_TEST_RUN}}` wrapper sentence, the `FLAGS:` classes, "**Only the two allowed comments.**", the probe-restore sentence, and the "**This step replaces a case.**" lead — each live in exactly one file under prompts/, every other template or partial reaching it through `{{INCLUDE:…}}`, with any wording that differed between copies left in the file that needs it, and every rendered prompt byte-identical to the merge base's ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 319 | 39 | 78 | 30804 | 3064730 | 158784 | 2.24 | 594 | unknown | unknown | unknown |  |  | full |
| for every phase and flag combination build-develop-prompt.test.sh, build-verify-prompt.test.sh and prompt-test-tiers.test.sh exercise, the rendered prompt is byte-identical to the merge base's, and those suites' assertions are unchanged except a case that pinned a passage's file location rather than the rendered text ⟦diff-checked⟧ ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 136 | 28 | 54 | 14160 | 1413624 | 122485 | 1.29 | 101 | unknown | unknown | unknown |  |  | full |
| build-verify-prompt.sh's argument list is unchanged from the merge base: no new positional, flag or environment input ⟦diff-checked⟧ ⟦criterion 5⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 37 | 10 | 20 | 2836 | 354774 | 110742 | 0.86 | 56 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| build-develop-prompt.sh replaces a `{{INCLUDE:<file>}}` token in a template with the contents of `skills/tdd/scripts/prompts/<file>` (trailing newlines stripped, as `$(cat …)` does), before every other substitution, so a placeholder inside the partial is still filled | 1 | 0/5 | structural-owed | PASS | 0 | 38 | 0.51 |
| build-develop-prompt.sh resolves a `{{INCLUDE:<file>}}` token that appears inside an included partial, recursively | 1 | 0/5 | nothing-left | PASS | 0 | 45 | 0.57 |
| build-verify-prompt.sh replaces a `{{INCLUDE:<file>}}` token in a template, and inside an included partial recursively, with that partial's contents before every other substitution, taking no new parameter ⟦criterion 5⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 113 | 0.84 |
| a template or partial whose `{{INCLUDE:<file>}}` names a partial that does not exist makes build-develop-prompt.sh exit 2 with the missing file's path on stderr and nothing on stdout ⟦criterion 3⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 95 | 0.78 |
| a partial that includes itself, directly or through another partial, makes build-develop-prompt.sh exit 2 naming the file on stderr, with nothing on stdout, rather than looping ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 58 | 0.58 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
| issue | 0/3 | candidates-done |

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s | run 35 s | run 36 s | run 37 s | run 38 s | run 39 s | run 40 s | run 41 s | run 42 s | run 43 s | run 44 s | run 45 s | run 46 s | run 47 s | run 48 s | run 49 s | run 50 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 2 | 2 | 2 | 3 | 2 | 2 | 2 | 0 | 2 | 2 | 2 | 2 | 3 | 1 | 1 | 1 | 1 | 3 | 0 | 0 | 0 | 2 | 2 | 1 | 2 | 4 | 4 | 5 | 0 | 0 | 3 | 2 | 2 | 2 | 2 | 18 | 0 | 17 | 5 | 2 | 1 | 2 | 3 | 2 | 10 | 7 | 21 | 7 | 7 | 3 |
| fast | 15 | 15 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 15 | 16 | 16 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 3 | 2 | 1 | 2 | 2 | 2 | 3 | 3 | 6 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 340 | 668 | 155755 | 16995052 | 1960136 | 18.21 |
