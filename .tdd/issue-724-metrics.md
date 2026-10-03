### 📊 Metrics — issue 724

Wall time for the issue: 3307 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 10 of 12 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/789.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 26 | 23 | 3 | 6 | 2278 | 114331 | 44098 | 0.42 |
| diff | 6 | 3 | 0 | 0 | 140 | 89 | 22 | 44 | 7119 | 901110 | 254982 | 2.36 |
| red | 8 | 1 | 0 | 0 | 392 | 323 | 71 | 138 | 29492 | 3632964 | 391797 | 4.45 |
| green | 2 | 1 | 0 | 0 | 200 | 93 | 23 | 46 | 9657 | 1247402 | 99182 | 1.24 |
| refactor | 2 | 1 | 0 | 0 | 101 | 43 | 12 | 24 | 4045 | 567706 | 89264 | 0.91 |
| pin | 6 | 6 | 0 | 0 | 206 | 155 | 32 | 62 | 13951 | 1389330 | 263275 | 2.66 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 13 | 13 | 0 | 0 | 513 | 318 | 67 | 132 | 28805 | 2964470 | 572775 | 5.75 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 552 | 408 | 96 | 188 | 37737 | 4888373 | 569823 | 6.29 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| extract-result.sh is removed from migration slice 3's list in tests/unit/missing-argument-exit.test.sh, in a commit of its own that precedes the port and changes nothing else, the slice's other scripts staying listed ⟦diff-checked⟧ ⟦criterion 1⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 19 | 8 | 16 | 2009 | 331964 | 81181 | 0.76 | 66 | unknown | unknown | unknown |  |  | full |
| veri.extract_result.main(argv), given a stream-json stream on stdin whose result record carries `VERDICT: PASS`, writes `VERDICT: PASS` and a newline on stdout and returns 0 (tests/py/test_extract_result.py); extract-result.sh becomes a /bin/sh shim that execs python3 on veri/extract_result.py once per invocation, holding no Python source, keeping its lowercase `usage:` header line and citing no issue number in any comment, with no wrapper turning an uncaught exception into exit 2; every case in tests/extract-result.test.sh passes with its assertions unmodified, the commit touching suites only in copy lines and stub libs ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 190 | 48 | 96 | 18045 | 2448788 | 279522 | 3.09 | 480 | unknown | 0/5 | nothing-left |  |  | full |
| extract-result.sh, run through a symlink to the skill directory and from another working directory, writes the same stdout and exit code as when run in place (a case in tests/extract-result.test.sh) ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 18 | 34 | 7513 | 882295 | 94807 | 1.09 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/extract-result.test.sh holds a case per exit code and the argument floor: a result record whose `result` is a number exits 1 with a traceback on stderr, and an extra argument is ignored, stdin still being extracted with exit 0 ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 14 | 26 | 5828 | 633806 | 90849 | 0.97 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_extract_result.py asserts through veri.extract_result.main what 'extracts result text', 'multiline result unescaped', 'escaped quotes survive' and 'last result wins' assert ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 71 | 17 | 34 | 7078 | 876283 | 96051 | 1.09 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_extract_result.py asserts through veri.extract_result.main what the seven #624 report cases assert: a developer report, a SPLIT: report, a TEST_PATH: report and a SUITE:-only report each beat a later record with no report line; of two records both carrying a report line the later wins; a VERDICT: record beats a later record without one; with no report line in any record the last record wins ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 62 | 12 | 24 | 5443 | 593757 | 94416 | 0.98 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_extract_result.py asserts through veri.extract_result.main what '#624 a developer report with no result record passes through unchanged', 'passthrough non-stream' and 'json but no result event' assert ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 73 | 13 | 26 | 5077 | 640094 | 92099 | 0.97 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/py/test_extract_result.py pins the ported quirks through veri.extract_result.main: a result record whose `result` is null, or that has no `result` key, counts as no result, so a stream of only such records passes through unchanged; a non-string `result` raises out of main rather than being mapped to 2; the report pattern is case-insensitive and allows leading spaces or tabs; the result gets a trailing newline only when it lacks one; empty stdin gives empty stdout and returns 0; arguments are ignored ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 83 | 16 | 30 | 8161 | 762379 | 95774 | 1.08 | unknown | unknown | unknown | unknown |  |  | pin |
| tests/extract-result.test.sh keeps only the floor — the exit-0 'extracts result text' case, the exit-1 non-string result case, the extra-argument case and the symlink case — with every other case, each replaced by a tests/py/test_extract_result.py case, removed, and no remaining case's assertions changed ⟦diff-checked⟧ ⟦criterion 4⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 44 | 7 | 14 | 2739 | 289176 | 92789 | 0.85 | 76 | unknown | unknown | unknown |  |  | full |
| skills/tdd/scripts/veri/leaf_log.py, tests/run-leaf.test.sh and tests/harvest-usage.test.sh are unchanged by the branch, tests/supervise.test.sh and tests/run-verdict.test.sh are changed at most in lines that copy scripts into a scratch directory, and tests/unit/missing-argument-exit.test.sh is changed only by the removal of extract-result.sh from migration slice 3's list ⟦diff-checked⟧ ⟦criterion 5⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 26 | 7 | 14 | 2371 | 279970 | 81012 | 0.75 | 55 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| veri.extract_result.main(argv), given a stream-json stream on stdin whose result record carries `VERDICT: PASS`, writes `VERDICT: PASS` and a newline on stdout and returns 0 (tests/py/test_extract_result.py); extract-result.sh becomes a /bin/sh shim that execs python3 on veri/extract_result.py once per invocation, holding no Python source, keeping its lowercase `usage:` header line and citing no issue number in any comment, with no wrapper turning an uncaught exception into exit 2; every case in tests/extract-result.test.sh passes with its assertions unmodified, the commit touching suites only in copy lines and stub libs ⟦criterion 2⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 101 | 0.91 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 4 | 3 | 1 | 0 | 1 | 4 | 3 | 5 | 2 | 2 | 1 | 0 | 0 | 4 |  |  |  |  |  |  |  |  |  |  |
| fast | 38 | 40 | 42 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| target | 0 | 2 | 1 | 1 | 1 | 1 | 2 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 0 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 163 | 320 | 66542 | 7852843 | 1142598 | 12.04 |
