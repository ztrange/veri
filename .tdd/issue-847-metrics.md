### 📊 Metrics — issue 847

Wall time for the issue: 3222 s, from the last `resume`, or the first event of the log when there is none, to the mark that ended the run.
Seconds the machine was not running inside that span: 0 s, excluded from it.
Steps done: 6 of 13 planned.
Outcome: the run landed — its draft PR is https://github.com/ztrange/veri/pull/857.
Cost is every leaf of the run, and the conductor own spending is not in it: this log carries no usage record of the conductor own.
Models requested: VERI_MODEL unset, VERI_MODEL_DEVELOPER unset, VERI_MODEL_VERIFIER unset; models that answered: claude-opus-5-5.

#### By phase

| phase | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| plan | 2 | 1 | 1 | 0 | 75 | 65 | 6 | 12 | 6779 | 244697 | 94871 | 0.94 |
| cover | 6 | 0 | 0 | 0 | 129 | 90 | 21 | 42 | 8788 | 880658 | 265565 | 2.48 |
| transform | 12 | 6 | 0 | 0 | 1506 | 307 | 83 | 166 | 30308 | 3987932 | 538675 | 5.71 |

#### By model

| role | model | attempts | PASS | REJECT | kills | wall s | API s | turns | input | output | cache read | cache creation | $ |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| verifier | claude-opus-5-5 | 8 | 7 | 1 | 0 | 834 | 211 | 45 | 90 | 20168 | 2066897 | 360322 | 3.70 |
| developer | claude-opus-5-5 | 12 | 0 | 0 | 0 | 876 | 251 | 65 | 130 | 25707 | 3046390 | 538789 | 5.43 |

#### Rework and waste, by phase

| phase | rework wall s | rework $ | waste wall s | waste $ |
| --- | ---: | ---: | ---: | ---: |
| plan | 0 | 0.00 | 0 | 0.00 |
| cover | 0 | 0.00 | 0 | 0.00 |
| transform | 0 | 0.00 | 0 | 0.00 |

#### By step

| step | attempts | PASS | REJECT | kills | retries | no-verdict | API s | turns | input | output | cache read | cache creation | $ | wall s | revise | refactor | stopped | crossed at | split | kind |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | --- | --- | --- | --- |
| Extract Class `RestAdapter` for reads: the REST driver's read work moves out of the public functions into methods of one `class RestAdapter` — the `page=N` paging loop with `&page=` after an existing `?`, the empty-page pattern and `NoAnswer(answer)` carrying pages already read (from `gh_rest_list`), and the `gh api …/issues/<n>` call, its JSON decode line on stderr and its reshaping (`null` body → `"\n"`, labels one per line) (from `gh_issue_view`'s fallback branch) — and those public functions call the adapter instead, signatures and return values unchanged. Predicate: `grep -q '^class RestAdapter' F && ! awk '/^def gh_/,/^$/' F | grep -E 'json\.loads|page=' > /dev/null` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 73 | 18 | 36 | 6794 | 844841 | 134047 | 1.38 | 384 | unknown | unknown | unknown |  |  | full |
| Move Method: `gh_issue_edit`'s PATCH (`gh api -X PATCH …/issues/<n> -F body=@<file>`) and `gh_issue_create`'s POST (`gh api …/issues -f title=… -f body=… -q .html_url`) move into `RestAdapter` methods, and both public functions call the adapter, signatures, return values and `NoAnswer` raises unchanged. Predicate: `grep -q '^class RestAdapter' F && ! awk '/^def gh_/,/^$/' F | grep -E '_gh(_api)?\(' > /dev/null` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 63 | 19 | 38 | 6226 | 894361 | 131430 | 1.35 | 400 | unknown | unknown | unknown |  |  | full |
| Extract Class `GraphQLAdapter`: the `gh issue|pr …` calls with stderr dropped (`gh_list`'s `_gh_graphql(*args)` and `gh_issue_view`'s `issue view <n> --json <field> -q <query>`) move into methods of one `class GraphQLAdapter`, each raising `NoAnswer("")` on a non-zero exit, and `gh_list`/`gh_issue_view` call it, falling to `RestAdapter` on its `NoAnswer`. Predicate: `grep -q '^class GraphQLAdapter' F && ! awk '/^def gh_/,/^$/' F | grep -E '_gh_graphql|returncode' > /dev/null` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 70 | 20 | 40 | 7369 | 965708 | 138132 | 1.45 | 300 | unknown | unknown | unknown |  |  | full |
| Replace the two inline fallbacks with a composed `class FallbackAdapter(first, second)`: its list and issue view try `first` and on its `NoAnswer` ask `second`; its REST-only operations (paged REST list, issue edit, issue create) go to `second` directly with no GraphQL attempt; `gh_list` and `gh_issue_view` lose their inline try/fallback and delegate to it, and the adapter carries no copy of either driver's `gh` invocation, paging or REST-answer parsing. Predicate: `grep -q '^class FallbackAdapter' F && ! awk '/^def gh_/,/^$/' F | grep -E 'except|GraphQLAdapter' > /dev/null && ! awk '/^class FallbackAdapter/,/^class [^F]|^def /' F | grep -E '_gh|page=|json\.loads' > /dev/null` ⟦criterion 2⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 67 | 17 | 34 | 6984 | 798907 | 136374 | 1.39 | 227 | unknown | unknown | unknown |  |  | full |
| Extract Class `FixtureAdapter`: a `class FixtureAdapter`, given the fixture directory, answers `<directory>/<fixture>`'s contents and starts no process; `gh_json` reads the file through it instead of opening it itself, behaviour unchanged. Predicate: `grep -q '^class FixtureAdapter' F && ! awk '/^def gh_json/,/^$/' F | grep -E 'open\(' > /dev/null` ⟦criterion 1⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 45 | 14 | 28 | 4425 | 617511 | 128403 | 1.24 | 185 | unknown | unknown | unknown |  |  | full |
| Introduce one selection function `_select`: `_select` alone reads `VERI_GH_JSON`, at call time, and alone constructs adapters — the fixture adapter for `gh_json` when it is set, `FallbackAdapter(GraphQLAdapter(), RestAdapter())` otherwise, and the fallback adapter for every other operation whether or not it is set (so `gh_issue_view`/`gh_issue_edit` still run `gh` with it set); `gh_json` with no gh args still goes straight to REST. No public function reads the environment or constructs an adapter. Predicate: `grep -q '^def _select' F && ! awk '/^def gh_/,/^$/' F | grep -E 'VERI_GH_JSON|environ|Adapter\(' > /dev/null && [ "$(grep -c VERI_GH_JSON F)" -eq "$(awk '/^def _select/,/^$/' F | grep -c VERI_GH_JSON)" ]` ⟦criterion 3⟧ | 3 | 1 | 0 | 0 | 0 | 0 | 79 | 16 | 32 | 7298 | 747262 | 135854 | 1.38 | 269 | unknown | unknown | unknown |  |  | full |

The figure comparable across runs is turns, the same measurement on any model; dollars are not comparable, the same measurement only at the same VERI_MODEL, VERI_MODEL_DEVELOPER and VERI_MODEL_VERIFIER.

#### Structural pass

Stopped: nothing-structural

#### Test-command seconds, by tier

| tier | run 1 s | run 2 s | run 3 s | run 4 s | run 5 s | run 6 s | run 7 s | run 8 s | run 9 s | run 10 s | run 11 s | run 12 s | run 13 s | run 14 s | run 15 s | run 16 s | run 17 s | run 18 s | run 19 s | run 20 s | run 21 s | run 22 s | run 23 s | run 24 s | run 25 s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| affected | 1 | 44 | 101 | 101 | 1 | 79 | 40 | 35 | 10 | 2 | 49 | 17 | 1 | 1 | 97 | 100 | 1 | 39 | 82 | 1 | 40 | 64 | 0 | 73 | 81 |

#### Total

| run | turns | input | output | cache read | cache creation | $ |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| total | 110 | 220 | 45875 | 5113287 | 899111 | 9.13 |
