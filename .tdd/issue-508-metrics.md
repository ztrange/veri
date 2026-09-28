### 📊 Metrics — issue 508

Wall time for the issue: 7718 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 4 of 4 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/541.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 11 | 2 | 4 | 1126 | 56634 | 37128 | 0.33 |
| red | 7 | 3 | 0 | 0 | 722 | 248 | 59 | 116 | 24423 | 2890674 | 324944 | 3.67 |
| green | 6 | 3 | 0 | 0 | 4974 | 324 | 88 | 174 | 30906 | 4313782 | 277074 | 3.70 |
| refactor | 6 | 3 | 0 | 0 | 944 | 174 | 51 | 100 | 16962 | 2288470 | 249295 | 2.79 |
| pin | 1 | 1 | 0 | 0 | 206 | 32 | 8 | 16 | 3299 | 357544 | 42839 | 0.48 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |
| pin | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| When a suite's last line of output is not a count line, `make test` still prints a line beginning `<suite>: never reached its count line` and that failure also quotes the suite's last output line verbatim ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 263 | 68 | 134 | 24665 | 3338569 | 273958 | 3.35 | 2983 | unknown | 1/5 | nothing-structural |  |  | full |
| When a suite prints no output at all, `make test` reports its output as empty rather than quoting an empty line ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 205 | 55 | 108 | 20086 | 2519461 | 257868 | 2.97 | 1119 | unknown | 1/5 | nothing-structural |  |  | full |
| When a suite prints only blank lines, `make test` reports its output as empty rather than quoting an empty last line ⟦added⟧ ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 235 | 66 | 130 | 23202 | 3165056 | 269285 | 3.25 | 2655 | unknown | 1/5 | nothing-structural |  |  | full |
| When a suite's last line is its `<n> passed, <m> failed` count line, `make test` prints no never-reached-its-count-line failure for it, exactly as before ⟦criterion 3⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 75 | 17 | 34 | 7637 | 827384 | 93041 | 1.06 | unknown | unknown | unknown | unknown |  |  | pin |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| When a suite's last line of output is not a count line, `make test` still prints a line beginning `<suite>: never reached its count line` and that failure also quotes the suite's last output line verbatim ⟦criterion 1⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 316 | 0.89 |
| When a suite prints no output at all, `make test` reports its output as empty rather than quoting an empty line ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 288 | 0.96 |
| When a suite prints only blank lines, `make test` reports its output as empty rather than quoting an empty last line ⟦added⟧ ⟦criterion 2⟧ | 1 | 1/5 | nothing-structural | PASS | 0 | 340 | 0.95 |

#### Structural pass

| pass | refactor | stopped |
| --- | ---: | --- |
