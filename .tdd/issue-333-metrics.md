### 📊 Metrics — issue 333

Wall time for the issue: 2442 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Steps done: 5 of 5 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/349.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| red | 6 | 1 | 0 | 0 | 484 | 384 | 59 | 112 | 37377 | 2975685 | 326501 | 5.69 |
| green | 2 | 1 | 0 | 0 | 414 | 90 | 12 | 24 | 8964 | 547931 | 90611 | 1.40 |
| refactor | 2 | 1 | 0 | 0 | 194 | 35 | 10 | 18 | 3262 | 351501 | 76402 | 1.02 |
| pin | 4 | 4 | 0 | 0 | 452 | 126 | 26 | 52 | 11380 | 1124775 | 172941 | 2.58 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| skill-leaf-env.test.sh's 10 launches (case 1's 5 developer lines and case 2's 5 verifier lines) all overlap: a start and a finish marker each launch writes show every launch's start marker preceding every launch's finish marker ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 198 | 35 | 66 | 19239 | 1423081 | 250689 | 3.70 | 1337 | unknown | 1/5 | nothing-structural |
| with launches concurrent, a launch whose leaf does not see VERI_TEST_CMD is still reported by skill-leaf-env.test.sh against the launch line it came from, by line number ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 119 | 19 | 36 | 11839 | 953546 | 107785 | 1.85 | unknown | unknown | unknown | unknown |
| case 3 of skill-leaf-env.test.sh still reads all 10 launch trees' event logs only after every launch has completed, with its assertions unchanged ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 125 | 22 | 42 | 11107 | 1124625 | 107201 | 1.91 | unknown | unknown | unknown | unknown |
| one launch line's sentinel deliberately broken is reported naming that one line, while the other 9 launches still pass ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 97 | 15 | 30 | 9747 | 732880 | 106507 | 1.68 | unknown | unknown | unknown | unknown |
| skill-leaf-env.test.sh's count line and every existing problem/report message format are unchanged, and make test is green ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 96 | 16 | 32 | 9051 | 765760 | 94273 | 1.55 | unknown | unknown | unknown | unknown |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 107 | 206 | 60983 | 4999892 | 666455 | 10.69 |
