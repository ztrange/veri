### 📊 Metrics — issue 628

Wall time for the issue: 2581 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 1 s, excluded from it.
Steps done: 4 of 7 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/732.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 1 | 1 | 0 | 0 | 26 | 23 | 2 | 4 | 2165 | 56895 | 43140 | 0.40 |
| cover | 4 | 0 | 0 | 0 | 372 | 63 | 16 | 32 | 6287 | 660346 | 166184 | 1.59 |
| transform | 8 | 4 | 0 | 0 | 884 | 157 | 40 | 80 | 16907 | 1742729 | 330615 | 3.33 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 5 | 5 | 0 | 0 | 578 | 91 | 20 | 40 | 9248 | 800681 | 202624 | 1.97 |
| developer | claude-opus-5-5 | 8 | 0 | 0 | 0 | 704 | 152 | 38 | 76 | 16111 | 1659289 | 337315 | 3.35 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Function: `solvable-issues.sh`'s `gh_json` moves into `lib/github.sh` as `gh_json <fixture-file> <rest-path> [gh args…]` (fixture when `VERI_GH_JSON` is set, otherwise `gh_list <rest-path> <gh args…>`), with a header entry in the file's one-entry-per-function form citing no issue number, and `solvable-issues.sh` calls it with the full `repos/${repo:-…}/…` rest path and its `repo_args` — predicate: `grep -v '^[[:space:]]*#' skills/tdd/scripts/lib/github.sh | grep VERI_GH_JSON > /dev/null && ! grep -v '^[[:space:]]*#' skills/tdd/scripts/solvable-issues.sh | grep -E 'VERI_GH_JSON|gh_json\(\)' > /dev/null` ⟦criterion 3⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 63 | 15 | 30 | 7084 | 668992 | 129126 | 1.31 | 372 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call in `workqueue.sh`: `lib/github.sh`'s `gh_json`, given no gh arguments, calls `gh_rest_list <rest-path>` and never `gh` itself or `gh_list`, and `workqueue.sh next` reads its issues through `gh_json issues.json "repos/{owner}/{repo}/issues?state=all&per_page=100"` with no gh arguments — predicate: `! grep -v '^[[:space:]]*#' skills/tdd/scripts/workqueue.sh | grep -E 'VERI_GH_JSON|gh_rest_list|gh_list|issue list' > /dev/null` ⟦criterion 4⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 65 | 14 | 28 | 6568 | 597182 | 122363 | 1.23 | 222 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call in `invisible-work.sh`: its own `gh_json` is deleted and both listings call `lib/github.sh`'s with the full `repos/{owner}/{repo}/…` rest path — predicate: `! grep -v '^[[:space:]]*#' skills/tdd/scripts/invisible-work.sh | grep -E 'VERI_GH_JSON|gh_json\(\)' > /dev/null` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 47 | 14 | 28 | 4956 | 597900 | 123941 | 1.21 | 249 | unknown | unknown | unknown |  |  | full |
| Replace Inline Code with Function Call in `parallel-conductors.sh`: the open-PR listing asks `lib/github.sh`'s `gh_json prs.json "repos/{owner}/{repo}/pulls?state=open&per_page=100" pr list --state open --limit 10000 --json body,isDraft,url` instead of choosing between the fixture and `gh_list` itself — predicate: `! grep -v '^[[:space:]]*#' skills/tdd/scripts/parallel-conductors.sh | grep VERI_GH_JSON > /dev/null` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 45 | 13 | 26 | 4586 | 539001 | 121369 | 1.17 | 566 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 11 | 38 | 178 | 13 | 13 | 60 | 22 | 32 | 32 | 30 | 31 | 32 | 93 | 92 | 91 | 98 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 58 | 116 | 25359 | 2459970 | 539939 | 5.32 |
