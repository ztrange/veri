# veri — working notes for agents

A Claude Code skill suite that solves one GitHub issue under strict TDD. The whole
product is `skills/tdd/`: a procedure in English (`SKILL.md`) that Claude
follows, plus seventy-two bash scripts it calls — seventy, strictly: `invisible-work.sh` and
`unreachable.sh` are counted with them but the procedure never calls them; they are maintenance
utilities a human or a loop runs, the first to report a branch no PR was opened for, or one not
on `origin` (#197), the second to list the scripts no declared entry point reaches (#498). Read
`CONTEXT.md` for the glossary — the terms there (conductor, leaf, supervisor, verdict, ledger, bail) are used precisely everywhere.

## Commands

The two test tiers veri detects when run against its own repo (#338):

veri: fast tests: `make unit`
veri: all tests: `make test`

| | |
|---|---|
| `make test` | The shell unit suites. **This is also the command veri detects when run against its own repo**, so it must stay green — a red baseline makes the conductor refuse to start. |
| `make install-dev` | Creates the one virtual environment the pytest leg runs in, at `$VERI_VENV` (default `~/.veri-tools/venv`, outside every worktree, so every worktree and run shares one install), and installs `requirements-dev.txt` — pytest, pinned to one exact version — with that environment's own pip. Run once per machine; run again over an existing environment it exits 0. Nobody activates it: `make unit` and `make test` find it themselves. It ends by printing the `export PATH="<venv>/bin:$PATH"` line that puts it first on PATH, for the scripts that run `python3` from PATH; when `run-conductor.sh` or `leaf-launchable.sh` refuses an interpreter below the 3.12 floor, a second line names `$VERI_VENV/bin` if that venv meets it. |
| `make docs` | Regenerate `docs/walkthrough.html` from the scripts. The committed page is what `.github/workflows/pages.yml` publishes to <https://ztrange.github.io/veri/> — **by hand only** (`gh workflow run pages.yml`); the workflow has no trigger but `workflow_dispatch`, so a merge never deploys. The site is public although the repo is private, a deliberate choice recorded in that workflow's header. |
| `make install-hooks` | Installs the `reference-transaction` hook that says so when a version tag arrives the built page does not list. Run once per clone; `.git/hooks` is shared, so it covers every worktree. Refuses rather than clobbering a hook it does not recognise. |
| `make merge-gates` | **Run before merging any PR**, in its worktree on the rebased tip. Diffs the branch against `origin/main` and runs only the docs gates the changed files warrant: nothing for a README change, **nothing for a change under `skills/`** (#125 — a development PR no longer owes a page; the lag is debt `docs/docs-owed.sh` files instead), **nothing for a change under `docs/adr/`** (#146 — the build reads no ADR, so one can neither make the page stale nor move a guard, and a development PR recording a decision should not pay ~5 min for it; `docs/tests/docs-gap-adr.test.sh` still covers ADRs in the docs lane's own runs), **nothing for a `Makefile` change** (#164 — the page goes stale by design on every tag and every script change; the freshness check on a development branch therefore failed for what `main` did while the branch was open, whatever the recipe edit was, and a broken docs target is the docs lane's to catch on its own cadence), `docs-fresh` (~2 s) for a hand-edited page, and `make docs-test` (every suite under `docs/tests/`, ~2 min) plus `docs-fresh` for a change anywhere else under `docs/` **except** `walkthrough.html` itself, which is the build's output rather than one of its inputs (#137 — the rule is the directory, not a list of its parts, so a script or suite added there is gated by existing). Exit 1 names the failing gate and, for a stale page, the fix. `VERI_GATES=all` forces both. |
| `make docs-fresh` | Rebuild once and compare to the committed page — the half of `docs-check` that a merge usually owes. |
| `make docs-check` | Two phases: the docs build guards still fire, then the committed page still matches a fresh build — and still agrees with the phases `build-verify-prompt.sh` accepts and the revise budget `SKILL.md` sets. |

`docs-check` is deliberately **not** part of `test`, for the reason in the row above:
documentation drifting behind code must never block a TDD run. Since 2026-09-11 it is not
in CI either: its thirty sandboxed page builds made every job ~4× longer on both runners.
`make merge-gates` runs the right subset of it at merge time; CI runs `make test` only, on
Linux only — the BSD-tools half of the portability promise is covered by the development
machine being a Mac, not by a runner (macOS minutes bill at 10× Linux). And never on a
draft PR (since 2026-09-27): a veri run pushes its draft 20–40 times per issue, each push
ran the job, and none of those runs gated anything — so CI runs when the PR is marked
ready, on each push after that, and on `main`.

**veri needs bash 5 or newer** (since 2026-09-18; it promised bash 3.2 before). On a Mac,
`brew install bash` — it lands ahead of `/bin/bash`, macOS's 3.2, on PATH. Nothing tests veri
on an older bash, so the three places a run or a test run begins refuse one outright, naming
that install line: `make test`, `run-conductor.sh` and `leaf-launchable.sh` (exit 2), pinned by
`bash-version-guard.test.sh`.

## The one trap

**`docs/walkthrough.html` is generated. Never edit it by hand** — `make docs-check` will
fail, and your edit is lost on the next `make docs`. To change that page:

- prose, per-script commentary → `docs/wt/commentary.py` (chunks keyed by line range)
- how the source is coloured → `docs/wt/bashlex.py` (four token classes, no more)
- the bash reference entries → `docs/wt/primer.py`
- styling / the tooltip layer → `docs/wt/style.css`, `docs/wt/app.js`
- then `make docs`

The build **fails rather than emitting a wrong page** if a `{{p-id|…}}` names an entry
that does not exist, or if a commentary chunk claims lines a script does not have. What it
no longer fails on is a line **no** chunk claims (#125): that line renders as it always
does, its note column says `commentary owed`, and the build prints `owed: <script>
L<a>–<b>` on stderr and exits 0. Prose is allowed to lag behind code — the page's promise
is that the source is verbatim, not that someone has explained it yet.

**Every line above is the documentation lane's work, and a development run is not in it**
(#143). A leaf or conductor step of a `/tdd` run whose test command is not a `make docs-*`
target never edits the page or its inputs and never runs `make docs` — the target refuses
with exit 2, because `VERI_TEST_CMD` in its environment says a development run typed it.
The regen recipe under "Versions are tags, and nothing else" is the same rule: it types
`make docs` like any other caller, so it runs from a human's shell or a docs issue's run,
never from a development one.

## Exit codes are the API

Every script speaks the same four codes, and the conductor branches on them. Preserve this
when touching any script:

| | |
|---|---|
| `0` | success, or `PASS` |
| `1` | a clean negative — the leaf ran and failed, the verifier said `REJECT`. A real answer. |
| `2` | **no answer could be obtained** — killed-stuck, unparseable verdict, bad arguments |
| `3` | nothing to do — no unchecked step, no matching checkbox. Not an error. |

The gap between `1` and `2` is the load-bearing one: it is the difference between a
**process** failure (the methodology spoke) and a **system** failure (the plumbing broke),
which `classify-bail.sh` turns into the label a human reads. Never collapse them.

## Versions are tags, and nothing else

A version is an annotated git tag `vN.M` whose **message is the capability**, in the issue's
own words. There is no `VERSION` file, no changelog, and nothing to keep in sync: the
walkthrough's capability index is computed from the tags and the `feat:`/`fix:` commits in
each tag's range. One merged issue is one capability is one minor bump; documentation, test
and refactor PRs get no tag, because a version means what veri can *do* changed.

The tag is cut when a PR lands (the `merge` skill does it), not in a separate release step.
Two traps, both already cost something once:

- **`git tag --sort=-v:refname`, never plain `sort`** — lexically `v0.9` outranks `v0.10`.
- **Backfilling needs `GIT_COMMITTER_DATE`** — an annotated tag's date is the *tagger's*,
  so retro-cut tags otherwise all claim to have shipped today.
- **A regen commit built at the tag isn't the fixpoint.** `unreleased` is `HEAD !=
  latest tag's commit` (`docs/wt/gitmeta.py:128`), so a commit made there says "not
  unreleased" and then falsifies itself — `docs-check` goes red again (#52, #53).
  Recipe: `make docs && git commit`, then `make docs && git commit --amend --no-edit`
  — the amend runs one commit past the tag, so the page already says Unreleased and
  stays byte-stable until the next tag. The post-tag hook prints its reminder either way.

## Invariants worth not breaking

- **A run executes one skill snapshot.** `run-conductor.sh` pins the skill to the commit in
  `.tdd/issue-<n>-skill-commit` and refuses (exit 2) a recorded commit the clone cannot
  resolve; only `VERI_NEW_SKILL=1` re-pins, logged as a `skill-repin` event. The mechanism is
  documented under *Launching the conductor* in `skills/tdd/SKILL.md`.

- **Every leaf is launched through `supervise.sh`** — never `run-leaf.sh` or `claude`
  directly. Stuck-detection policy lives in exactly one place only because nothing
  bypasses it.
- **The verifier is blind by construction.** `build-verify-prompt.sh` takes only a phase,
  the spec file, the test path and a test id. There is no parameter for the developer's
  rationale, so it cannot leak. Adding one would silently end the guarantee. The `refactor`
  phase takes `<base-sha>`, the step's green commit, in place of the test id (#151): it must
  match `^[0-9a-f]{7,40}$` or the builder exits 2, so the only thing that parameter can carry
  is a hex commit name, never the developer's rationale — and the verifier reads
  `git diff <base-sha>..HEAD`, not the range's commit messages.
- **The committed ledger is the source of truth** for which steps are done, ticked
  atomically with each step's green commit; the GitHub issue only mirrors it. That tick
  also appends `⟂ refactor pending`, which only that step's verify-refactor PASS takes off
  again — so a ticked step is green, not finished, and the mark is what tells a resumed run
  which of the two it is.
- **Five budgets on five axes, never merged**: `VERI_STUCK_RETRIES` (liveness — the leaf
  never answered), `VERI_NO_VERDICT_RETRIES` (protocol compliance — the verifier finished
  cleanly and ignored the output contract, no `VERDICT:` line), `REVISE_BUDGET` (verdict — it
  answered and was rejected), `VERI_REFACTOR_BUDGET` (cost — how many transforms one step's
  tidying is worth, since one refactor leaf now spends the whole step's budget and a leaf
  given a number will find that many) and `VERI_STEP_GROWTH` (plan growth — how many steps
  one ledger may hold marked `⟦added⟧`, so a run that discovers work as it goes can grow
  its plan without growing it without end; ADR-0022). The fifth is never merged with the
  other four either: folded into any of them, "let the run plan more" and "let a leaf retry,
  revise or refactor more" would be one decision. One knob over any two of them would trade a plumbing
  failure against a methodology one, or against how much a step is allowed to cost; over the
  first two, "retry more hangs" (a hung tool, fixed in the supervisor's windows) and
  "tolerate more contract breaches" (a model choice, fixed in the prompt) would be the same
  decision (ADR-0020). A bad `VERI_REFACTOR_BUDGET` is caught
  in preflight, not mid-launch, which is why the refactor phase can treat
  `refactor-budget.sh` exit 2 as impossible. ADR-0017, superseding ADR-0010, is where one
  leaf for the step rather than one per transform is recorded.
- **The developer's model and the verifier's are separate knobs**, for the same reason the
  budgets above are never merged: the two roles fail differently. `VERI_MODEL` sets every
  leaf's model, `VERI_MODEL_DEVELOPER` only a developer leaf's (`develop-*`, `revise-*`)
  and `VERI_MODEL_VERIFIER` only a verifier's (`verify-*`), a role variable beating the
  general one. A cheaper **verifier** is legible in the run log as a changed verdict
  distribution; a cheaper **developer** shows up as more revise cycles and worse code, which
  costs the saving back. One knob over both would make "cheaper developer" and "weaker
  verifier" the same decision, and no run log could tell them apart afterwards. The measured
  first experiment is `VERI_MODEL_VERIFIER`; all three ship unset, so a default run's
  `claude` command line carries no `--model` at all.
- **Selection is three bands, one sort key.** `solvable-issues.sh` prints its scope as the
  issues labelled `priority` first, then the `bug`s, then the rest, each band ascending by
  number; `VERI_PRIORITY_LABEL` names the first band's label (default `priority`,
  set-but-empty is exit 2) and the second band's is GitHub's own `bug`. The band reorders
  the solvable set and never enlarges it: the four conditions — open, opted in, unblocked,
  unclaimed — run first and the sort runs on what survives, so `priority` says *take it
  sooner* where only `VERI_LABEL` says *may veri take this at all*. Labelling `priority`
  alone must never make an issue takeable, which is the whole reason the sentence is here
  and not just in the script.
- **A walkthrough build asks git once per script, once per tag, and eight times besides.**
  `docs/tests/build-guards.test.sh` pins that as a budget. Every question is a process
  (~30 ms), so a question asked per commit or per blamed line — `tag --contains`, `show
  --name-only` — is what made a build 16 s and `make docs-test` the cost of every leaf
  on a docs issue. Ask it of the table `gitmeta._shipped()` already built instead.
- **A tag is the one input to the page that changes without a commit.** The capability
  index is built from `git tag`, so cutting one leaves `docs/walkthrough.html` behind
  and `make docs-check` red until someone runs `make docs`. That window is deliberate —
  `docs-check` is not part of `test` — so the hook only *notices*; it never rebuilds or
  commits, because which PR carries the rebuild is a judgement.

## Testing idiom

Plain-shell asserts, zero dependencies, under
`skills/tdd/scripts/tests/` — 144 files for seventy-two scripts, plus thirty-one suites under `unit/` (five moved there, two written for them, fourteen written with the script or helper they test — `step-cost.test.sh`, `step-budget.test.sh`, `run-affordable.test.sh`, `cover-outcome.test.sh`, `comment-class.test.sh`, `ledger.test.sh`, `github.test.sh`, `exit-contract.test.sh`, `candidate-line.test.sh`, `window.test.sh`, `section-end.test.sh`, `frontmatter-name.test.sh`, `fenced-lines.test.sh` and `venv-python.test.sh` — and two written for the argument contract they all share — `missing-argument-exit.test.sh`, which audits it over every script, and `missing-argument-guard.test.sh`, which plants an offender so that audit is known to go red — one written to pin the text veri emits, `emitted-text.test.sh`, one written to pin where the pending mark is spelled, `pending-mark-literal.test.sh`, one written with the sourced test harness, `harness.test.sh`, one written to pin that no suite carries its own `report`, `no-report-copies.test.sh`, one written to pin that no suite copies a script into a scratch tree without the lib it sources, `scratch-copy-libs.test.sh`, and one written with the sourced guard-plant library, `guard-plant.test.sh`, and one written with the check that every develop prompt asking for a commit states the `(#<issue>)` suffix, `commit-suffix.test.sh`), all run by `make test`.
`supervise.sh` has a second suite for its retry axis, and two suites belong to no single
script: `hermetic-suites.test.sh` is a cross-suite test that pins the suites' independence
from ambient `VERI_*` tunables, and `workflow-timeouts.test.sh` is the first to assert on
something outside `skills/` at all — it reads `.github/workflows/ci.yml` as text, the way
GitHub Actions does, and pins what the `gates` job declares and why (issue #99). All
keep `pass`/`fail` counters, print `FAIL - <name>` with a diff, and end with a count.
Match that style rather than introducing a framework.

**The four `-recorded` suites no longer keep their own counters** — the rule that they did
came from #225, whose only reason was no framework and no outside dependency, and #496
retired it: `lib/harness.sh` is in-repo plain shell, `record-helpers.sh` sources it, and
those suites count through it like every other.

Ending on the count line is not a formatting convention — **the `test` recipe enforces it**. A suite
whose output does not end in `<n> passed, <m> failed` fails the run, named:
`<suite>: never reached its count line`. A suite's **exit code alone is not trusted**
because a suite that dies partway routinely comes back 0 — under `set -u`, which every
suite here declares, a word rather than a number inside `[[ … -le … ]]` is read as a
variable name, an unset name kills the script, and the script then exits with the status of
the command *before* the comparison. `build-guards.test.sh` ran 37 of its 54 cases that way
until commit `c4a6bdb`, and the run still said `all suites green` (#157). A non-zero exit
still fails a suite, count line or not; the check lives in the recipe once, so a suite added
under the glob is covered by existing.

**That same `pipefail` is why a suite never ends a pipeline in `grep -q` or `head`** (#422).
Both readers leave before EOF, so a writer with bytes still to push dies of SIGPIPE on the
closed pipe, `pipefail` hands that 141 up as the pipeline's status, and the assertion built on
it is inverted — green on this Mac, where BSD grep's ~16 kB buffer lets the writer finish in
one `write()`, and red on CI, where glibc's 4 kB pipe buffer makes it two. Repair by letting
the reader consume to EOF (`grep -F … > /dev/null` in place of `grep -qF …`) or by feeding it
with a redirection rather than a pipe, which moves the status off the writer — never with
`trap '' PIPE` or by dropping `pipefail`, which is what makes the rest of these suites honest
(#157). `no-sigpipe-pipelines.test.sh` fails the run naming `<suite>:<line>`, against an
exemption table carrying a reason per entry, the way `no-nested-suites.test.sh` does.

**A background process is killed by the pid recorded when it started, never by a job spec**
(#424). `kill %…` names a row in the job table of the shell that started the process, and
that table dies with the shell: once it is gone the number means nothing, the child is
reparented to PID 1, and nothing is left that knows its identity — which on 2026-09-22 left
ten orphaned busy-loops at ~988% of CPU for twelve hours, quietly distorting every timing
this repository measures, `make profile` included. Start it with `bg_start` and end it with
`bg_kill` from `lib/background.sh`: a pid is a system-wide name, so the kill lands from any
shell. The EXIT trap `bg_start` arms only *reports* a survivor by pid and command on the
starting shell's stderr — a killed process's own cleanup never runs, so a trap is a warning
someone can act on, never the thing that guarantees the child dies.
`no-job-spec-kills.test.sh` fails the run naming `<file>:<line>`, against an exemption table
carrying a reason per entry.

**No suite relies on permission bits to make a path unreadable or unwritable** (#846).
`chmod 000`, `chmod a-r`, `chmod u-w` or a read-only directory forces a failure only for an
ordinary user: the cloud runs as root, uid 0 ignores permission bits, so there the chmod is a
no-op, the read succeeds, and the case goes red — which made `make test` red in every cloud
session and stopped `/tdd` at preflight. The same holds for a system location (#860): under uid
0 every path is writable and readable, so a case that expects creating `/.tdd`, or reading
`/root` or `/proc`, to fail passes nothing there — it succeeds, and leaves its write behind at
the filesystem root. A forced failure has to come from the file's type or the path's shape,
never from permissions or from the path being a system location: make the path a directory so
the read raises `IsADirectoryError`, or put a regular file where a directory would be created
so mkdir fails, inside the case's own scratch tree. Never skip the case when `$EUID` is 0,
which leaves the failure path untested exactly where it broke.
`no-permission-bits.test.sh` fails the run naming `<suite>:<line>`, for a chmod and for a
system path alike, against an exemption table carrying a reason per entry.

**`skills/tdd/scripts/tests/unit/` is the fast tier**, run alone by `make unit` and also by
`make test`. A suite belongs there only if it clears the admission bar: about 100 ms per
case, and no git, network, servers, real waits (`sleep`) or nested suites — judged by
grepping the suite's own source, not by timing it, and stated in its header. `make unit`
shims `git`, `gh`, `curl` and `python3` so a suite that calls one for real fails, named, and
`make test` applies the same shims to the suites under `tests/unit/` only, never to another
suite; a unit suite mocks them as shell functions instead. The one `python3` call the guard
lets through is one whose first argument is a module file under `skills/tdd/scripts/veri/` —
the hand-off a ported script's shim makes — so a unit suite can run a ported script through its
entry point; every other `python3` call is refused, named and logged. Everything else stays in
`tests/`.

**`make unit` and `make test` also run a pytest leg** over `skills/tdd/scripts/tests/py/`, when a `test_*.py` is there; with none, both targets answer as they did before it. A pytest suite's admission rule is no process but the interpreter: under `make unit` a case that starts `git`, `gh` or `curl` fails, naming the command, while the bash suites under `tests/unit/` keep the refusing `python3` shim. The leg runs with `$VERI_VENV/bin/python3` (default `~/.veri-tools/venv`), the environment `make install-dev` creates, falling back to the `python3` on PATH, and sees the recipe's `LC_ALL=C`, stdin and offline settings, plus a fresh `PYTHONPYCACHEPREFIX` the recipe removes on exit: a verifier that mutates a module and reverts it within the same second, at the same size, would otherwise leave a stale `.pyc` the next run reuses (#1127, #873). Two refusals, both exit 2 before any suite runs: pytest cannot be imported (stderr names pytest and `make install-dev`; `VERI_PYTEST_IMPORTABLE` stands in for the answer), or the interpreter is older than the Python 3.12 floor (stderr names the floor and the version found; `VERI_PYTHON_VERSION` stands in).

**A script moves into the unit tier by one pattern** (#339). The script's logic goes behind
functions, and a main guard — `[[ "${BASH_SOURCE[0]}" == "$0" ]] && main "$@"` — is the only
code that runs when it is executed. A new `tests/unit/<script>.test.sh` sources the script,
never execs it, and mocks every command it shells out to as a same-named shell function, so
those calls start no process. The CLI contract — arguments, stdout, stderr, exit codes — stays
byte-identical, proven by the script's integration suite passing unmodified in `tests/`, where
it stays. `push-branch.sh` was its first example and has left it, ported to Python under the
convention `status.sh` is the worked example of (#720). What still follows it is a library:
`lib/github.sh`, sourced by `tests/unit/github.test.sh` with `gh` mocked as a shell function.

**A script ported to Python follows one convention, and `status.sh` is its worked example**
(#634). Its logic moves into a module of the `skills/tdd/scripts/veri/` package, and its
`.sh` entry point stays, as a `/bin/sh` shim that `exec`s `python3` on that module once per
invocation, so its Bash holds no Python source — no heredoc fed to `python3`, no
`python3 -c` string. A ported script's tests live in `tests/py/test_<module>.py`, which
imports the module and fakes only process boundaries; its bash suite under `tests/` keeps
the contract cases that run it through its entry point.

**A suite whose subject is the docs pipeline lives in `docs/tests/`, not here**, and runs by
existing — `make docs-test` globs that directory, so a suite added there owes no Makefile
edit (#137). Per step, the red and refactor leaves run the affected suites — the one holding
the new case, the ones covering the files a transform touched (#144) — and `develop-green`
and the two blind verifiers (verify-green and verify-refactor) run the fast tier plus the
affected suites; a revise leaf runs the tiers of the phase it redoes. `make test` is the
**full suite**, and the conductor runs it once per PR,
before the PR is readied, plus once per repair step a red result there appends (#539), plus once
more on the rebased tip when the Draft PR step had to rebase the branch (#1026) — so a
docs suite under `make test`'s glob still taxes every PR's full run, and every step whose
affected set names it, with a tool that is not functional (ADR 0016). `docs-guard-filter.test.sh` and `docs-owed.test.sh` were moved out on
2026-09-12 for that reason: together ~30 s of an 81 s `make test`. `docs-gap-adr.test.sh`
followed on 2026-09-13 — its subject is a record under `docs/adr/`, and the only thing that
had kept it here was the recipe line the glob replaced. `suite-lanes.test.sh`, also under
`docs/tests/`, pins the line: it reads both targets' rosters off `make -n` and fails if
anything `make test` runs declares a docs subject.

**And a suite here never reads a path in the generated tree** — not the committed page, not
a generator input, not for one figure quoted in prose. `no-docs-reads.test.sh` fails the run
naming the suite and the line when one does (#143); a path only written into a fixture as
text is not a read. What catches prose lagging behind code is the documentation lane's own
work, not a case here: `docs/docs-owed.sh` reports the chunks a script is owed, and
`docs-fresh` goes red at a docs merge when the committed page no longer matches a fresh
build.

Where a test would otherwise need a real model or a real clock, it injects instead:
`CLAUDE_BIN` swaps in a stub binary, and `VERI_HEARTBEAT` / `VERI_TIMEOUT` /
`VERI_STUCK_RETRIES` shrink the supervisor's windows, and `VERI_FETCH_RETRY_SLEEP` the conductor's
ref-lock fetch retry, so nothing waits on wall time. That
is why every tunable is read as `${VAR:-default}`.

**A suite asserts behaviour** — outputs, exit codes, files and events the unit under test
produces; process counts, fork counts and timings are observed with `make profile` and
reported in a speed PR's body, never pinned in a suite; **no suite runs another suite.**
`no-nested-suites.test.sh` fails the run naming `<suite>:<line>` and the suite it names,
against an exemption table it carries with a reason for each — the plants that have to run a
real suite to prove a fragile seam still catches a regression, or a runner's own verdict over
a real tree, both of which no cheaper read establishes. metrics-python3-starts.test.sh,
harvest-usage-launch.test.sh and probe-suites-unchanged.test.sh (#331) copied a real suite
into a scratch tree and reran the whole thing, sometimes several times over, to pin a
python3-start count or a case roster: ~41.5s of `make test` to pin a ~1.5s saving. They are
gone, not exempted; the one behaviour among their assertions no remaining case covered — that
run-leaf.sh's appended result text keeps a leaf's closing record from ever being its log's
last line — moved into harvest-usage.test.sh's own first case. `supervise.test.sh`'s own
former case 33 (#290's "one supervision starts at most 1 python3" ceiling, a PATH shim
counting processes over the whole suite) is gone the same way, not moved: the behaviour it
protected — that event.sh's bash rewrite still escapes a payload byte-identical to
`json.dumps`'s own — is pinned independently by `tests/py/test_event.py`'s
`test_main_escapes_every_string_by_the_bash_table_over_the_argument_and_variable_bytes`. When a call
count IS itself the behaviour (a launcher that must be called exactly once per mark, say),
the code calls one wrapper function and the test replaces that wrapper with a spy function
that records its calls, in-process — never a PATH shim counting processes over a suite run.

A guard or a failure path that has never been watched to fail is not tested. Break it on
purpose, see the test go red, put it back.

## `make test` on the development Mac

It measured 393–515 s here against 176 s on CI on 2026-09-18 (the same 76 suites), and
154 s here against a 55 s CI `gates` job on 2026-09-19, after #314–#327. Five causes were
Mac-only, and none of them is the suites' own work:

- **bash 3.2** — `/bin/bash` is the one macOS ships, and it is slow where the suites are busy:
  a pattern substitution over CLAUDE.md's 17.5 kB took 3.86 s on it and ~0.2 s on bash 5.
  veri now requires bash 5 (`brew install bash`) and refuses to run a suite without it.
  Homebrew's bash 5 is slower to *start*, though — 12 ms against `/bin/bash`'s 4 ms in
  Ghostty, because it loads its own libraries and CoreFoundation — and a run started 4,834
  bash processes. So a suite's own stubs are `#!/bin/sh` (#322), and a helper a script calls
  per leaf is a function sourced from `scripts/lib/` rather than a script it forks (#323).
- **Locale, stdin and git** — the `test` recipe fixes all three for every suite (`LC_ALL=C`,
  `< /dev/null`, a resolved-and-symlinked `git`), and `make-test-env.test.sh` pins them. BSD
  text tools run ~12× slower in UTF-8; an inherited stdin let a stub `claude`'s `cat` block a
  leaf's backgrounded `make test` for 28 minutes; `/usr/bin/git` is xcrun's own shim, costing
  ~21 ms a call on top of the real binary, so the recipe resolves it once with `xcrun -f git`
  and puts a plain symlink to the answer first on every suite's PATH. That symlink used to be
  a bash wrapper instead — `tests/offline/git`, refusing a remote URL by pattern-matching the
  git verb — and cost ~26 ms/call against ~8 ms for the real binary, 1,820 of a run's 4,834
  bash starts (measured 2026-09-18). It is gone: refusing a remote reach is now git's own
  `protocol.allow=never` / `protocol.file.allow=always` (set via the same GIT_CONFIG_COUNT
  mechanism as `http.proxy`), and a suite whose fetch is refused no longer gets a named
  "tried the network: …" line the way one that calls gh or curl still does — those two stay
  bash shims, since they are not the hot path. `count-line-guard.test.sh` pins both halves.
- **The first run of a new executable** — macOS checks every newly written or copied
  executable the first time it runs: ~330 ms each, against ~5 ms afterwards. The suites write
  stubs and copy the skill per case. The fix is a machine setting, not code: run
  `sudo spctl developer-mode enable-terminal`, then enable the terminal that launches veri
  under System Settings → Privacy & Security → Developer Tools, and restart it. Ghostty is
  enabled here, measured at 5 ms, including for a child detached with `setsid` as
  `detach-leaf.sh` does. **A Claude desktop session is not covered**: the app launches
  commands through a `disclaimer` helper that makes a versioned `claude.app` under
  `~/Library/Application Support/Claude/claude-code/` responsible, and that path changes on
  every update. Launch conductors from the enabled terminal.

The suites that waited on a real clock now run on an injected one (#314–#317, #325), and the
ones that ran a whole other suite to check one property run the slice they check (#324, #327).
What is left is per-case process work — a server started, a python3 per assertion, a fork per
file. None of it is fixed by an acceptance criterion measured in seconds on this machine —
#282 bailed twice on exactly that — and a process count pinned in a suite is the same mistake
the other way round (a suite asserts behaviour, not cost: see "Testing idiom"). So a veri
issue about speed states its acceptance criteria as behaviours only; the speed itself is
`make profile` run before and after, quoted in the PR body and read before merging, never
asserted as a test. CI's `timeout-minutes` stays the only wall-clock gate.
