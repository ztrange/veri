### 📊 Metrics — issue 723

Wall time for the issue: 4873 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 14 of 17 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/788.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 66 | 57 | 4 | 8 | 5209 | 128341 | 87151 | 0.83 |
| red | 14 | 3 | 0 | 0 | 582 | 458 | 106 | 210 | 42396 | 5315952 | 655510 | 7.16 |
| pin | 8 | 8 | 0 | 0 | 217 | 165 | 34 | 68 | 16075 | 1446775 | 340765 | 3.34 |
| green | 10 | 3 | 2 | 0 | 848 | 322 | 80 | 158 | 28448 | 4007249 | 378853 | 4.40 |
| refactor | 6 | 3 | 0 | 0 | 300 | 131 | 33 | 66 | 10747 | 1530476 | 266795 | 2.66 |
| diff | 6 | 3 | 0 | 0 | 205 | 102 | 27 | 54 | 10207 | 1299328 | 283404 | 2.73 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 24 | 21 | 3 | 0 | 1169 | 627 | 126 | 252 | 55386 | 5782143 | 966652 | 10.00 |
| developer | claude-opus-5-5 | 22 | 0 | 0 | 0 | 1049 | 608 | 158 | 312 | 57696 | 7945978 | 1045826 | 11.11 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |
| green | 679 | 3.47 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| tier-usual.sh run with no argument exits 2 with nothing on stdout and stderr exactly the one line `usage: tier-usual.sh <tier>` (a floor case in tests/tier-usual.test.sh, written against the bash script before the port) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 13 | 24 | 4359 | 573554 | 88700 | 0.91 | unknown | unknown | unknown | unknown |  |  | pin |
| tier-usual.sh <tier>, run where `.tdd/events.jsonl` holds no `test-run` event for that tier, exits 1 with nothing on stdout (a floor case in tests/tier-usual.test.sh, written against the bash script before the port) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 45 | 12 | 24 | 4531 | 565301 | 86721 | 0.90 | unknown | unknown | unknown | unknown |  |  | pin |
| tier-usual.sh, run through a symlink to the skill directory and from another working directory, prints the same stdout and exit code as when run in place, for a tier with test-run events and for a missing argument (a case in tests/tier-usual.test.sh) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 97 | 15 | 30 | 9716 | 841191 | 103780 | 1.19 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.tier_usual.main([]) returns 2 with nothing on stdout and `usage: tier-usual.sh <tier>` on stderr (tests/py/test_tier_usual.py), and tier-usual.sh is removed from migration slice 9's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying ⟦criterion 1⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 223 | 60 | 118 | 21038 | 2918009 | 318043 | 3.55 | 623 | 1/2 | 0/5 | nothing-left |  |  | full |
| veri.tier_usual.main(["fast"]), run in a working directory under tmp_path whose `.tdd/events.jsonl` holds more than 10 test-run events for tier fast interleaved with events of another tier and of another kind, returns 0 and prints the median of the `seconds` of that tier's last 10 test-run events in log order — for that even window the mean of the two middles, `5.5` for the log tests/tier-usual.test.sh pins (tests/py/test_tier_usual.py, faking only the working directory and files under tmp_path, never patching a function of veri.tier_usual) ⟦criterion 4⟧ | 8 | 3 | 1 | 0 | 0 | 0 | 254 | 56 | 112 | 19956 | 2820174 | 334711 | 3.64 | 583 | 1/2 | 0/5 | nothing-left |  |  | full |
| veri.tier_usual.main(["fast"]) over a log holding an odd number (fewer than 10) of fast test-run events returns 0 and prints the middle one of them sorted (tests/py/test_tier_usual.py, faking only the working directory and files under tmp_path, never patching a function of veri.tier_usual) ⟦criterion 4⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 147 | 37 | 74 | 12438 | 1737233 | 264113 | 2.71 | 470 | unknown | 0/5 | nothing-left |  |  | full |
| veri.tier_usual.main(["fast"]) prints its figure as Python's float repr, so a whole median prints with a trailing `.0` (e.g. `4.0`) (tests/py/test_tier_usual.py, faking only the working directory and files under tmp_path, never patching a function of veri.tier_usual) ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 51 | 12 | 24 | 5031 | 564431 | 88560 | 0.92 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.tier_usual.main(["fast"]) when `.tdd/events.jsonl` holds no test-run event for the tier raises out of main — no conversion to a return code — and prints nothing on stdout (tests/py/test_tier_usual.py, faking only the working directory and files under tmp_path, never patching a function of veri.tier_usual) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 49 | 11 | 22 | 4670 | 512799 | 87763 | 0.90 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.tier_usual.main(["fast"]) when `.tdd/events.jsonl` does not exist raises out of main — no conversion to a return code — and prints nothing on stdout (tests/py/test_tier_usual.py, faking only the working directory and files under tmp_path, never patching a function of veri.tier_usual) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 57 | 13 | 26 | 5520 | 627106 | 90660 | 0.96 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.tier_usual.main(["fast"]) when a line of `.tdd/events.jsonl` is not JSON raises out of main — no conversion to a return code — and prints nothing on stdout (tests/py/test_tier_usual.py, faking only the working directory and files under tmp_path, never patching a function of veri.tier_usual) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 53 | 12 | 24 | 5380 | 570158 | 90203 | 0.94 | unknown | unknown | unknown | unknown |  |  | pin |
| veri.tier_usual.main(["fast"]) when a matching test-run event's `seconds` is not a number raises out of main — no conversion to a return code — and prints nothing on stdout (tests/py/test_tier_usual.py, faking only the working directory and files under tmp_path, never patching a function of veri.tier_usual) ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 50 | 12 | 24 | 5027 | 570496 | 88669 | 0.92 | unknown | unknown | unknown | unknown |  |  | pin |
| tier-usual.sh is a /bin/sh shim that execs python3 on veri/tier_usual.py once per invocation, holding no Python source, keeping the lowercase `usage: tier-usual.sh <tier>` line in its header and citing no issue number in any comment; veri/tier_usual.py imports event_log from the package and carries no wrapper turning an uncaught exception into exit 2; every case in tests/tier-usual.test.sh passes with its assertions unmodified, in a commit that precedes any cut, whose diff, in the test suites, touches only copy lines and stub libs and changes no assertion ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 56 | 13 | 26 | 5372 | 710291 | 104859 | 1.09 | 140 | unknown | unknown | unknown |  |  | full |
| tests/tier-usual.test.sh holds the survivors and the floor — the median case (exit 0), the no-test-run-event case (exit 1), the exact missing-argument stderr case (exit 2) and the symlink case — with no pre-existing case's assertions changed ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 8 | 16 | 2316 | 361925 | 98060 | 0.90 | 49 | unknown | unknown | unknown |  |  | full |
| tests/timed-test-run.test.sh, tests/over-budget.test.sh and tests/unit/emitted-text.test.sh are unchanged by the branch (so emitted-text's `3568418922 35` pin for tier-usual.sh stays in place), and tests/unit/missing-argument-exit.test.sh is changed only by the removal of tier-usual.sh from migration slice 9's list ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 23 | 6 | 12 | 2519 | 227112 | 80485 | 0.74 | 70 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.tier_usual.main([]) returns 2 with nothing on stdout and `usage: tier-usual.sh <tier>` on stderr (tests/py/test_tier_usual.py), and tier-usual.sh is removed from migration slice 9's list in tests/unit/missing-argument-exit.test.sh in the same commit, the slice's other scripts staying ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 92 | 0.88 |
| veri.tier_usual.main(["fast"]), run in a working directory under tmp_path whose `.tdd/events.jsonl` holds more than 10 test-run events for tier fast interleaved with events of another tier and of another kind, returns 0 and prints the median of the `seconds` of that tier's last 10 test-run events in log order — for that even window the mean of the two middles, `5.5` for the log tests/tier-usual.test.sh pins (tests/py/test_tier_usual.py, faking only the working directory and files under tmp_path, never patching a function of veri.tier_usual) ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 117 | 0.89 |
| veri.tier_usual.main(["fast"]) over a log holding an odd number (fewer than 10) of fast test-run events returns 0 and prints the middle one of them sorted (tests/py/test_tier_usual.py, faking only the working directory and files under tmp_path, never patching a function of veri.tier_usual) ⟦criterion 4⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 91 | 0.89 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s | run 26 s | run 27 s | run 28 s | run 29 s | run 30 s | run 31 s | run 32 s | run 33 s | run 34 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 0 | 0 | 1 | 8 | 14 | 6 | 5 | 8 | 5 | 0 | 7 | 1 | 1 | 2 | 2 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 44 | 0 | 10 |
| target | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 0 |  |  |  |  |  |  |  |  |  |  |  |  |  |
| fast | 38 | 41 | 40 | 41 | 39 | 38 | 38 | 39 | 40 | 44 | 42 | 45 | 43 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 284 | 564 | 113082 | 13728121 | 2012478 | 21.11 |
