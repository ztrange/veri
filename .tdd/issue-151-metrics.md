### 📊 Metrics — issue 151

Wall time for the issue: 19550 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 7 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/284.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 13 | 6 | 0 | 0 | 1562 | 491 | 102 | 180 | 41342 | 4376368 | 536186 | 6.00 |
| green | 15 | 6 | 1 | 0 | 12324 | 769 | 145 | 272 | 47774 | 7046892 | 525600 | 7.97 |
| refactor | 12 | 6 | 0 | 0 | 3863 | 614 | 115 | 230 | 52437 | 6504113 | 518661 | 5.38 |
| pin | 1 | 1 | 0 | 0 | 337 | 37 | 15 | 26 | 3207 | 760917 | 45423 | 0.37 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 4491 | 3.23 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| build-verify-prompt.sh refactor takes a base sha as its 4th argument and puts it in the prompt ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 277 | 62 | 114 | 20694 | 3023179 | 247966 | 2.63 | 2084 | unknown | 0/5 | structural-owed |
| build-verify-prompt.sh refactor exits 2 with a stderr diagnostic when the base sha is missing or is not 7–40 lowercase hex characters ⟦criterion 1⟧ | 9 | 3 | 1 | 0 | 0 | 1 | 454 | 82 | 154 | 31256 | 3971616 | 322510 | 4.87 | 5281 | 1/2 | 1/5 | nothing-structural |
| verify-refactor.md has the verifier review git diff <base-sha>..HEAD and tells it not to read the range's commit messages ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 232 | 51 | 102 | 17061 | 2660144 | 237575 | 2.50 | 2963 | unknown | 0/5 | nothing-left |
| verify-refactor.md makes a removed or weakened test assertion a REJECT naming it, names cosmetic-only hunks in REASON without rejecting on them, and does not reject an empty range by itself ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 221 | 57 | 100 | 19208 | 2474024 | 231838 | 2.52 | 3234 | unknown | 0/5 | nothing-structural |
| verify.sh refactor passes the base sha through to the verifier prompt ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 75 | 22 | 40 | 7048 | 1064865 | 87904 | 1.04 | unknown | unknown | unknown | unknown |
| SKILL.md passes the step's green commit sha to verify.sh refactor at both call sites, the cycle loop and Resume sub-step 2's $green ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 383 | 69 | 134 | 34171 | 3902730 | 297140 | 3.36 | 2930 | unknown | 0/5 | nothing-structural |
| CLAUDE.md's blind-verifier invariant names the base-sha parameter and why a sha cannot leak rationale ⟦criterion 3⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 269 | 34 | 64 | 15322 | 1591732 | 200937 | 2.79 | 2143 | unknown | 0/5 | structural-owed |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 377 | 708 | 144760 | 18688290 | 1625870 | 19.71 |
