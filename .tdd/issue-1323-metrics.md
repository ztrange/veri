### 📊 Metrics — issue 1323

Wall time for the issue: 2452 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 3 of 3 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/1456.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER sonnet; models that answered: claude-opus-5-5, claude-sonnet-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 11 | 8 | 2 | 4 | 1012 | 58260 | 39505 | 0.17 |
| red | 2 | 0 | 0 | 0 | 146 | 137 | 24 | 46 | 13511 | 1466062 | 137829 | 1.67 |
| pin | 2 | 2 | 0 | 0 | 39 | 31 | 13 | 26 | 3897 | 587454 | 84247 | 0.43 |
| green | 4 | 2 | 0 | 0 | 244 | 97 | 32 | 62 | 9774 | 1512605 | 186361 | 1.53 |
| refactor | 4 | 2 | 0 | 0 | 165 | 92 | 27 | 52 | 9461 | 1275927 | 184562 | 1.54 |
| diff | 2 | 1 | 0 | 0 | 298 | 92 | 21 | 38 | 8031 | 1073362 | 105043 | 0.98 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-sonnet-5-5 | 8 | 8 | 0 | 0 | 322 | 114 | 43 | 82 | 14062 | 1791611 | 340852 | 1.68 |
| developer | claude-opus-5-5 | 7 | 0 | 0 | 0 | 581 | 343 | 76 | 146 | 31624 | 4182059 | 396695 | 4.64 |

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
| Which remote and local branches invisible-work.sh reports or leaves out is pinned by pytest cases in tests/py/test_invisible_work.py driving the CLI through run_cli, faking only process boundaries (a case needing real git marked @pytest.mark.process), asserting the same exit code, stdout and stderr — a branch on origin with no PR reported with its tip, commits ahead and issue state; one with an open PR left out; a tdd branch whose issue is not in the repository reported with issue state unknown and no traceback; a local branch absent from origin reported with its tip, the commits origin lacks and its worktree, or with no worktree when none holds it; a local branch origin carries left out; a branch whose PR is merged or closed left out, and the default branch left out; a local branch absent from origin whose PR was merged or closed not reported as an invariant-1 finding — and the bash cases are gone: replaces 'invisible-work.sh: a branch on origin with no PR is reported with its tip, its commits ahead and its issue's state', 'invisible-work.sh: a branch on origin whose PR is still open is left out of the report', 'invisible-work.sh: a tdd branch whose issue is not in the repository is reported with its issue state unknown, with no traceback', 'invisible-work.sh: a local branch absent from origin is reported with its tip, the commits origin lacks and its worktree', 'invisible-work.sh: a local branch that origin carries too is left out of the report', 'invisible-work.sh: a local branch absent from origin that no worktree holds is reported with no worktree', 'invisible-work.sh: a branch whose PR is merged or closed is left out of the report, and so is the default branch', 'invisible-work.sh: a local branch absent from origin whose PR was merged or closed is not reported as an invariant-1 finding' in skills/tdd/scripts/tests/invisible-work.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 177 | 43 | 86 | 16621 | 2234145 | 296154 | 2.53 | 649 | unknown | 0/5 | nothing-left |  |  | already-satisfied |
| invisible-work.sh's exit codes and the invariant each finding names are pinned by pytest cases in tests/py/test_invisible_work.py driving the CLI through run_cli, faking only process boundaries, asserting the same exit code, stdout and stderr — exit 0 when it printed a finding and 3 with empty stdout when there is nothing to report; exit 2 with a stderr diagnostic and empty stdout when the remote or gh cannot be read; exit 2 with empty stdout and stderr's last line exactly `invisible-work.sh: cannot reach origin` when origin cannot be reached; exit 2 with empty stdout when the VERI_GH_JSON directory's issues.json is not JSON; every finding naming the one invariant it breaks — an existing pytest case already pinning one named as its replacement rather than duplicated — and the bash cases are gone: replaces 'invisible-work.sh: exits 0 when it printed a finding and 3 with empty stdout when there is nothing to report', 'invisible-work.sh: exits 2 with a stderr diagnostic and empty stdout when the remote or gh cannot be read', 'invisible-work.sh: exits 2 with empty stdout and stderr's last line exactly 'invisible-work.sh: cannot reach origin' when origin cannot be reached', 'invisible-work.sh: exits 2 with empty stdout when the VERI_GH_JSON directory's issues.json is not JSON', 'invisible-work.sh: every finding names the invariant it breaks' in skills/tdd/scripts/tests/invisible-work.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 6 | 3 | 0 | 0 | 0 | 0 | 180 | 53 | 100 | 20022 | 2607903 | 296845 | 2.64 | 525 | unknown | 1/5 | nothing-left |  |  | already-satisfied |
| invisible-work.test.sh, left with its cases after :339, still passes, its helpers no remaining case uses are gone with the cases, no guard table, roster, workflow comment or CLAUDE.md count outside .tdd/ and docs/ names a removed case, and CLAUDE.md's suite counts match the tree ⟦diff-checked⟧ ⟦criterion 2⟧ | 2 | 1 | 0 | 0 | 0 | 0 | 92 | 21 | 38 | 8031 | 1073362 | 105043 | 0.98 | 321 | n/a | n/a | n/a |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### By refactor pass

| step | pass | refactor | stopped | verdict | revise | wall s | $ |
| --- | ---: | ---: | --- | --- | ---: | ---: | ---: |
| Which remote and local branches invisible-work.sh reports or leaves out is pinned by pytest cases in tests/py/test_invisible_work.py driving the CLI through run_cli, faking only process boundaries (a case needing real git marked @pytest.mark.process), asserting the same exit code, stdout and stderr — a branch on origin with no PR reported with its tip, commits ahead and issue state; one with an open PR left out; a tdd branch whose issue is not in the repository reported with issue state unknown and no traceback; a local branch absent from origin reported with its tip, the commits origin lacks and its worktree, or with no worktree when none holds it; a local branch origin carries left out; a branch whose PR is merged or closed left out, and the default branch left out; a local branch absent from origin whose PR was merged or closed not reported as an invariant-1 finding — and the bash cases are gone: replaces 'invisible-work.sh: a branch on origin with no PR is reported with its tip, its commits ahead and its issue's state', 'invisible-work.sh: a branch on origin whose PR is still open is left out of the report', 'invisible-work.sh: a tdd branch whose issue is not in the repository is reported with its issue state unknown, with no traceback', 'invisible-work.sh: a local branch absent from origin is reported with its tip, the commits origin lacks and its worktree', 'invisible-work.sh: a local branch that origin carries too is left out of the report', 'invisible-work.sh: a local branch absent from origin that no worktree holds is reported with no worktree', 'invisible-work.sh: a branch whose PR is merged or closed is left out of the report, and so is the default branch', 'invisible-work.sh: a local branch absent from origin whose PR was merged or closed is not reported as an invariant-1 finding' in skills/tdd/scripts/tests/invisible-work.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 0/5 | nothing-left | PASS | 0 | 68 | 0.69 |
| invisible-work.sh's exit codes and the invariant each finding names are pinned by pytest cases in tests/py/test_invisible_work.py driving the CLI through run_cli, faking only process boundaries, asserting the same exit code, stdout and stderr — exit 0 when it printed a finding and 3 with empty stdout when there is nothing to report; exit 2 with a stderr diagnostic and empty stdout when the remote or gh cannot be read; exit 2 with empty stdout and stderr's last line exactly `invisible-work.sh: cannot reach origin` when origin cannot be reached; exit 2 with empty stdout when the VERI_GH_JSON directory's issues.json is not JSON; every finding naming the one invariant it breaks — an existing pytest case already pinning one named as its replacement rather than duplicated — and the bash cases are gone: replaces 'invisible-work.sh: exits 0 when it printed a finding and 3 with empty stdout when there is nothing to report', 'invisible-work.sh: exits 2 with a stderr diagnostic and empty stdout when the remote or gh cannot be read', 'invisible-work.sh: exits 2 with empty stdout and stderr's last line exactly 'invisible-work.sh: cannot reach origin' when origin cannot be reached', 'invisible-work.sh: exits 2 with empty stdout when the VERI_GH_JSON directory's issues.json is not JSON', 'invisible-work.sh: every finding names the invariant it breaks' in skills/tdd/scripts/tests/invisible-work.test.sh ⟦replaces-case⟧ ⟦criterion 1⟧ | 1 | 1/5 | nothing-left | PASS | 0 | 97 | 0.85 |

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 7 | 7 | 7 | 0 | 5 | 5 | 0 | 5 | 0 | 0 | 58 |
| target | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 0 |
| fast | 24 | 25 | 25 | 23 | 24 | 25 | 24 | 24 |  |  |  |  |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 119 | 228 | 45686 | 5973670 | 737547 | 6.33 |
