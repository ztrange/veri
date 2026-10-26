### 📊 Metrics — issue 2429

Wall time for the issue: 1693 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/2454.
Lane: ready-for-agent:mu
Cost is every leaf of the run, and the conductor own spending.
Conductor own spending: $1.72 over 40 turns, in 1 sessions, on opus.
The Conductor own spending figure is estimated: the output tokens of a session without a result record are not yet known.
Conductor context: first turn 88488 tokens, largest 125867 tokens

#### Conductor per turn

| turn | dollars | context |
| --- | ---: | ---: |
| 1 | $0.57 | 88488 |
| 2 | $0.03 | 89466 |
| 3 | $0.03 | 91077 |
| 4 | $0.03 | 91985 |
| 5 | $0.02 | 92348 |
| 6 | $0.02 | 92636 |
| 7 | $0.02 | 92916 |
| 8 | $0.02 | 93654 |
| 9 | $0.02 | 94271 |
| 10 | $0.04 | 96707 |
| 11 | $0.03 | 98190 |
| 12 | $0.03 | 99415 |
| 13 | $0.03 | 100477 |
| 14 | $0.03 | 101474 |
| 15 | $0.03 | 102420 |
| 16 | $0.03 | 103889 |
| 17 | $0.03 | 104555 |
| 18 | $0.03 | 105148 |
| 19 | $0.03 | 105926 |
| 20 | $0.03 | 106736 |
| 21 | $0.03 | 107522 |
| 22 | $0.03 | 108433 |
| 23 | $0.03 | 109509 |
| 24 | $0.03 | 110513 |
| 25 | $0.03 | 111196 |
| 26 | $0.03 | 112018 |
| 27 | $0.03 | 112902 |
| 28 | $0.03 | 114112 |
| 29 | $0.04 | 115840 |
| 30 | $0.03 | 116767 |
| 31 | $0.04 | 118427 |
| 32 | $0.04 | 120099 |
| 33 | $0.04 | 121804 |
| 34 | $0.03 | 122529 |
| 35 | $0.04 | 123943 |
| 36 | $0.03 | 124215 |
| 37 | $0.03 | 124511 |
| 38 | $0.03 | 125027 |
| 39 | $0.03 | 125347 |
| 40 | $0.03 | 125867 |
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet, VERI_MODEL_REVISE unset; models that answered: claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 15 | 13 | 2 | 4 | 1215 | 31162 | 31770 | 0.09 |
| diff | 2 | 1 | 0 | 0 | 88 | 25 | 8 | 16 | 1799 | 192098 | 43070 | 0.14 |
| red | 4 | 2 | 0 | 0 | 103 | 86 | 16 | 32 | 6289 | 470183 | 79490 | 0.31 |
| green | 4 | 2 | 0 | 0 | 186 | 70 | 18 | 36 | 5150 | 506320 | 62401 | 0.26 |
| refactor | 3 | 1 | 0 | 0 | 54 | 24 | 11 | 20 | 2102 | 273250 | 45485 | 0.16 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 7 | 7 | 0 | 0 | 201 | 99 | 21 | 42 | 6437 | 524338 | 118123 | 0.41 |
| developer | claude-sonnet-5-5 | 7 | 0 | 0 | 0 | 245 | 119 | 34 | 66 | 10118 | 948675 | 144093 | 0.56 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| diff | 0 | 0.00 | 0 | 0.00 |
| red | 0 | 0.00 | 0 | 0.00 |
| green | 0 | 0.00 | 0 | 0.00 |
| refactor | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| The older wrong-argument-count case in `skills/tdd/scripts/tests/py/test_park_issue_process.py` asserts only the usage line's prefix `usage: park-issue.sh <issue-number> <cause> <unblock> [`, so it holds both for today's usage line and for one whose `[<pr>]` part names the number and the URL forms; test-only, no production change ⟦diff-checked⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 25 | 8 | 16 | 1799 | 192098 | 43070 | 0.14 | 128 | n/a | n/a | n/a |  |  | full |
| `park-issue.sh <n> <cause> <unblock> https://github.com/<owner>/<repo>/pull/<m>` adds the label `parked` to PR `<m>` through the same label write the number form makes (`issues/<m>/labels`, never `issues/https://…/labels`), exits 0, and the number form is unchanged; pinned by a case ⟦criterion 1⟧ | 5 | 2 | 0 | 0 | 0 | 0 | 78 | 19 | 38 | 4689 | 525227 | 82377 | 0.31 | 227 | unknown | 0/5 | nothing-left |  |  | full |
| A `<pr>` argument that is neither a whole number nor a `https://github.com/<owner>/<repo>/pull/<m>` URL (e.g. `pull/12`, `#12`, `https://github.com/o/r/issues/12`) makes `park-issue.sh` exit 2 with a usage line on stderr naming both forms (the number and the PR URL), before any gh call: it posts no comment and writes no label; the wrong-argument-count usage line, the shim's `# Usage:` header and the `skills/tdd/SCRIPTS.md` entry name both forms too; pinned by a case ⟦criterion 2⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 102 | 26 | 50 | 8852 | 724526 | 104999 | 0.42 | 296 | unknown | 1/5 | nothing-left |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER, VERI_MODEL_VERIFIER and VERI_MODEL_REVISE.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| `park-issue.sh <n> <cause> <unblock> https://github.com/<owner>/<repo>/pull/<m>` adds the label `parked` to PR `<m>` through the same label write the number form makes (`issues/<m>/labels`, never `issues/https://…/labels`), exits 0, and the number form is unchanged; pinned by a case ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | skipped | 0 | 9 | 0.05 |
| A `<pr>` argument that is neither a whole number nor a `https://github.com/<owner>/<repo>/pull/<m>` URL (e.g. `pull/12`, `#12`, `https://github.com/o/r/issues/12`) makes `park-issue.sh` exit 2 with a usage line on stderr naming both forms (the number and the PR URL), before any gh call: it posts no comment and writes no label; the wrong-argument-count usage line, the shim's `# Usage:` header and the `skills/tdd/SCRIPTS.md` entry name both forms too; pinned by a case ⟦criterion 2⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 45 | 0.11 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| fast | 17 | 17 | 17 | 19 | 18 | 19 | 17 | 19 |  |  |  |  |  |
| affected | 2 | 1 | 1 | 2 | 2 | 2 | 1 | 1 | 2 | 26 | 2 | 2 | 2 |
| target | 1 | 0 |  |  |  |  |  |  |  |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 55 | 108 | 16555 | 1473013 | 262216 | 0.97 |
