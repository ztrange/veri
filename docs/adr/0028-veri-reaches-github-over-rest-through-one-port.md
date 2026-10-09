# veri reaches GitHub over REST by default, through one port

veri reads and writes GitHub through `gh`, and `gh` offers two routes:
- **GraphQL**: the porcelain commands `gh issue view`, `gh issue list`, `gh pr list` and
  `gh pr ready`;
- **REST**: `gh api repos/{owner}/{repo}/…`.

Until now both `veri/github.py` and its bash twin `lib/github.sh` tried GraphQL first and fell
back to REST, with the two routes interleaved inside every function. From here on:
- GitHub is reached through **one port**, an interface with one adapter per route;
- **REST is the default route**;
- GraphQL is kept as an option, chosen with `VERI_GH_DRIVER`.

## Context

- **The cloud refuses GraphQL.** Claude Code cloud sessions refuse GitHub's GraphQL endpoint.
  That is why the REST fallback exists (#798), and why `no-graphql-gh-calls.test.sh` fails the
  run on any `gh issue`, `gh pr` or `gh repo` call outside `lib/github.sh`. A cloud test on
  2026-10-04 confirmed the fallback is load-bearing there: removing it would leave veri unable
  to read an issue in the cloud.
- **Every read in the cloud paid a failed call first.** With GraphQL tried first, each read
  started a `gh` process that was refused before REST answered.
- **Nothing veri does needs GraphQL.** Every GraphQL call has a REST route already. That
  includes marking a draft PR ready (`POST …/pulls/<n>/ccr/ready_for_review` in
  `lib/github.sh`'s `gh_pr_ready`), which is the usual GraphQL-only case.
- **GraphQL saves about one call per list, and veri rarely lists much.**
  - The readers a run or a queue refill touches list *open* items only:
    `solvable-issues.sh:86-87` and `parallel-conductors.sh:70`. On 2026-10-04 that was 71 open
    issues (PRs included) and 5 open PRs, one REST page each. REST therefore costs 2 calls (the
    page, plus the empty page that ends the list) against GraphQL's 1.
  - The only readers of full history are run by hand: `veri/invisible_work.py`, and
    `veri/workqueue.py`, which calls `gh_json` with no gh args and so was already REST-only.

## Decision

- **One port, three adapters** (#847): GraphQL, REST, and fixture (`VERI_GH_JSON`). In
  `veri/github.py` they are `GraphQLAdapter`, `RestAdapter` and `FixtureAdapter`. The old
  GraphQL→REST behaviour is a `FallbackAdapter` composed from the GraphQL and REST adapters,
  not a copy of them; `rest` is `RestOnlyAdapter`, which never starts a GraphQL call, and
  `graphql` is `GraphQLOnlyAdapter`, which keeps the REST-only operations on REST and gives
  every GraphQL route no fallback. One selection point,
  `_select`, chooses the adapter at call time, never at import. The module's public functions
  stay as a facade with their signatures unchanged. `lib/github.sh` has no adapter objects:
  the same choice is made by the guards `_gh_driver_known`, `_gh_graphql` and `_gh_rest`
  around each route.
- **The port takes driver arguments, for now.** Callers pass a REST path and a GraphQL argv
  (`gh_list(path, *args)`), not intents like "list open PRs". A port shaped around intents would
  change every caller, so it waits until #825 and #826 have moved every caller onto the facade.
- **`VERI_GH_DRIVER` picks the route** (#848) of every operation that has a GraphQL route
  (`gh_issue_view`, `gh_list`, `gh_json` with gh args, bash `gh_pr_ready`):

  | Value | Route |
  |---|---|
  | unset, or `rest` (**the default**) | REST only; no GraphQL `gh` command runs |
  | `auto` | GraphQL, then REST: the old behaviour, byte-identical |
  | `graphql` | GraphQL only; a GraphQL failure is a no-answer, with no `gh api` call |
  | empty, or any other value | no `gh` process starts; `NoAnswer` in Python, return 2 in bash, so a script on either twin exits 2; one stderr line naming the variable and the value |

  - The value is checked at call time, by the twin's own selection point, not in conductor
    preflight: the GitHub readers that drive the queue (`solvable-issues.sh`,
    `parallel-conductors.sh`, `workqueue.sh`) and `invisible-work.sh` run outside any
    conductor. This follows `VERI_PRIORITY_LABEL` and `VERI_LABEL`, which their reader
    refuses.
  - Operations with no GraphQL route (issue create and edit, `gh_rest_list`, `gh_json` with no
    gh args) use REST under every value; `graphql` does not invent a route for them.
  - `VERI_GH_JSON` still wins over every value for `gh_json`, in both twins: the fixture
    answers and no process starts.
  - Both twins honour the variable until the last bash caller is ported.
  - Nothing plumbs it: a leaf inherits `VERI_*` from the conductor's environment like every
    other tunable, and a case pins that a conductor child and a detached leaf both see it.
- **REST is the default, not just an option for the cloud.** The two choices compare like this:

  | Default | Mac and cloud | Cost |
  |---|---|---|
  | **REST** (chosen) | run the same code path | one extra call per listing on the Mac |
  | GraphQL first | run different routes | one refused call per read in the cloud |

  With a GraphQL-first default, the Mac would test a route the cloud never takes, and every
  cloud user would have to know to set a variable. Nothing detects the cloud: the choice is
  explicit, and a cloud session needs nothing set.
- **Removing GraphQL entirely was rejected.** The adapter costs little to keep, and it is the
  route back if GitHub ever offers something veri needs only through GraphQL.
- **Out of scope:** `veri/capture_spec.py` and `veri/coverage_blocker.py` still call `gh`
  themselves until #825 and #826 move them onto the facade. "No GraphQL under `rest`" means
  every call made through `veri/github.py` or `lib/github.sh`.

## Consequences

- The Mac and the cloud behave the same, so `make test` on the development machine exercises
  the route a cloud run takes.
- A full-history listing makes about 10 REST calls where GraphQL made 1. Only the hand-run
  utilities make one.
- The suites that pin the old fallback order set `VERI_GH_DRIVER=auto` themselves, and every
  suite gives the same result whatever value the caller's shell holds;
  `run-suite.sh` strips the caller's `VERI_*` before a suite starts, and `make hermetic` re-checks
  that on demand, as it does for `VERI_PRIORITY_LABEL`.
- Switching the default back is a one-line change at the selection point, not an edit in every
  function.
