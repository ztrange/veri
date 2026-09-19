### 📊 Metrics — issue 341

Wall time for the issue: 16842 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 11 of 11 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/369.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 22 | 11 | 0 | 0 | 861 | 674 | 134 | 262 | 66653 | 5901559 | 924597 | 13.86 |
| green | 28 | 11 | 3 | 0 | 8593 | 830 | 237 | 462 | 78091 | 10549831 | 1183233 | 19.06 |
| refactor | 24 | 11 | 1 | 0 | 3835 | 511 | 146 | 288 | 47152 | 6270651 | 938080 | 13.70 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 3167 | 9.74 | 0 | 0.00 |
| refactor | 646 | 2.49 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| SKILL.md's preflight baseline step names `--tier fast`'s command as what it runs and times, in wording a text-reading guard suite can pin ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 130 | 38 | 74 | 11844 | 1540290 | 239059 | 3.46 | 2594 | unknown | 0/5 | structural-owed |
| develop-red.md and verify-red.md name the affected-suites command, not a single hand-named suite, as what the red leaf and its verifier run ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 154 | 42 | 84 | 14211 | 1802233 | 232204 | 3.58 | 1226 | unknown | 0/5 | nothing-left |
| verify-refactor.md's checklist item 1 no longer says "the project's full test suite" and names the affected-suites command ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 136 | 36 | 72 | 12608 | 1470575 | 228322 | 3.33 | 982 | unknown | 0/5 | nothing-left |
| develop-refactor.md names the affected-suites command fed refactor-touched.sh's output as what the refactor leaf runs after each transform | 8 | 3 | 1 | 0 | 0 | 0 | 227 | 56 | 110 | 21072 | 2334177 | 315100 | 4.85 | 2065 | 1/2 | 2/5 | nothing-structural |
| develop-green.md and verify-green.md name the fast command plus the affected suites as what they run, not "the full suite" ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 207 | 57 | 114 | 20152 | 2773428 | 256159 | 4.45 | 1939 | unknown | 1/5 | structural-owed |
| SKILL.md's Draft PR section and its closing invariant both name `--tier all`'s command, run exactly once, as the only full-suite gate left in the cycle ⟦criterion 5⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 114 | 33 | 64 | 10918 | 1315401 | 232442 | 3.26 | 942 | unknown | 0/5 | nothing-left |
| A red result on the final full run adds a repair step to the ledger rather than bailing, with a unit-tier test added when the failure exposes a gap and the verifier judging the fix against the full command ⟦criterion 6⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 120 | 33 | 66 | 11364 | 1363300 | 227658 | 3.24 | 756 | unknown | 1/5 | nothing-left |
| A second red result on the full run after a repair step bails, naming every suite still red, not only the first ⟦criterion 7⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 105 | 30 | 60 | 8940 | 1155660 | 215488 | 2.96 | 749 | unknown | 0/5 | structural-owed |
| build-develop-prompt.sh accepts the new parameters the tiered templates require and exits 2 on a missing one, its existing cases still passing ⟦criterion 8⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 178 | 43 | 82 | 17068 | 1849334 | 257045 | 3.92 | 817 | unknown | 0/5 | nothing-left |
| build-verify-prompt.sh accepts the new parameters the tiered templates require and exits 2 on a missing one, its existing cases still passing ⟦criterion 8⟧ | 10 | 3 | 2 | 0 | 1 | 0 | 299 | 69 | 136 | 29047 | 3218965 | 451107 | 6.85 | 2872 | 2/2 | 3/5 | nothing-structural |
| run-conductor.test.sh asserts, per phase with a stub claude, which command (fast, affected, fast+affected, or all) that phase's launch was built with ⟦criterion 9⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 345 | 80 | 150 | 34672 | 3898678 | 391326 | 6.73 | 1687 | 1/2 | 2/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 517 | 1012 | 191896 | 22722041 | 3045910 | 46.62 |
