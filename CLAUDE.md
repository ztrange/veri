# veri — working notes for agents

A Claude Code skill suite that solves one GitHub issue under strict TDD. The whole
product is `skills/tdd/`: a procedure (`SKILL.md`) Claude follows, plus the scripts it calls,
which are Python modules behind `/bin/sh` shims. `invisible-work.sh` (#197),
`unreachable.sh` (#498), `test-ceiling.sh` (#4418) and `reject-breakdown.sh` (#4568) are maintenance utilities the procedure never calls. `CONTEXT.md` is the glossary; its terms (conductor, leaf,
supervisor, verdict, ledger, bail) are used precisely everywhere.
Two sections no leaf reads, "Versions are tags, and nothing else" and "`make test` on the
development Mac", live in [operator/MAINTAINING.md](operator/MAINTAINING.md).

## Commands

veri: fast tests: `make unit`
veri: all tests: `make test`
veri: one test file: `make test TESTS="$1"`
veri: quiet test files: `"${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3" skills/tdd/scripts/tests/leg/pytest_leg.py --subset -q --no-header -rfE --tb=no`

| | |
|---|---|
| `make test` | The full suite, and the baseline veri detects in its own repo: it must stay green, since a red baseline makes the conductor refuse to start. Preflight skips the baseline when CI's `CI` run concluded `success` on the exact commit, or this machine recorded a green baseline of the same tree, commands, skill pin and venv lock (`PREFLIGHT.md` step 3); anything less runs it. |
| `make unit` | The fast tier: `skills/tdd/scripts/tests/py/unit/` only, without the `process` and `tree_audit` cases. |
| `make install-dev` | Once per machine: creates the shared venv at `$VERI_VENV` (default `~/.veri-tools/venv`) and installs the hash-checked lock `requirements-dev.txt` (generated from `requirements-dev.in`, installed with `--require-hashes`). Idempotent, never activated; it prints the `export PATH=…` line for scripts that run `python3` from PATH. |
| `make profile` | Runs the suites `make test` runs and prints one line per case at or above `VERI_PROFILE_THRESHOLD` seconds, slowest first. Nothing gates on it. |
| `make unreachable` | Lists the scripts no declared entry point reaches, through `unreachable.sh`. |
| `make report` | Prints the `/vreport` figures, through `report.sh`. |
| `make ceiling` | Ramps `make test`'s workers (2, 4, 6, … up to the logical cores, or `MAX=<n>`), one full suite per step, through `test-ceiling.sh`, to find the highest count with no case timeout, and records it in `~/.veri-test-ceiling` (`VERI_TEST_CEILING_FILE`), with the full and fast tiers' idle durations, the seconds the ceiling step's `make test` and one `make unit` after the ramp took. With a cap set (below), the ramp stops at the cap, an odd one included, and says which bound stopped it. Hours on an idle machine; never in CI, and nothing gates on it. |
| `make watch` | Reruns `make unit` whenever a tracked file changes. Nothing gates on it. |
| `make run-finished ISSUE=<n>` | Says whether run `<n>` is safe to merge, through `run-finished.sh`. |
| `make ready-check` | Reports whether veri can run in this repository, through `ready-check.sh`. |

Operator sessions, and every subagent they brief, run with `$VERI_VENV/bin` (default
`~/.veri-tools/venv/bin`) first on PATH, since PATH's `python3` may lack pytest.

CI runs `make test` only, on Linux only, with `timeout-minutes` on every job; never on a draft PR,
and a newer push cancels a PR's in-progress run (never on `main`). It restores the bytecode cache the
last push to `main` saved; only such a push saves it.

**veri needs bash 5+** (`brew install bash` on a Mac): `make test`, `run-conductor.sh` and
`leaf-launchable.sh` refuse an older one (exit 2).

## Exit codes are the API

Every script speaks these four codes and the conductor branches on them:

| | |
|---|---|
| `0` | success, or `PASS` |
| `1` | a clean negative — the leaf ran and failed, the verifier said `REJECT`. A real answer. |
| `2` | **no answer could be obtained** — killed-stuck, unparseable verdict, bad arguments |
| `3` | nothing to do — no unchecked step, no matching checkbox. Not an error. |

Never collapse 1 and 2: a process failure (the methodology spoke) is not a system failure
(the plumbing broke); `classify-bail.sh` labels bails by it.

## Invariants worth not breaking

- **A run executes one skill snapshot.** `run-conductor.sh` pins the skill to the commit in
  `.tdd/issue-<n>-skill-commit` and refuses (exit 2) one the clone cannot resolve; only
  `VERI_NEW_SKILL=1`, or the `.tdd/issue-<n>-released` marker a successful `release-issue.sh <n>` leaves and the
  next launch consumes, re-pins (a `skill-repin` event). The snapshot is read-only, and a run stops (exit 2) when it
  changed since extraction: `supervise.sh` refuses the next launch, `run-conductor.sh` its exit.
- **A run's branch base is the conductor's record**, `.tdd/issue-<n>-branch-base` in the main working tree: written
  at the cut (`preflight.sh`) and by its own `rebase-onto-default.sh`, carried on `refs/veri/runs/<n>`, read back on
  a resume and never recomputed from a remote-tracking ref (exit 2 when missing or invalid). A leaf can rewrite refs.
- **Every leaf is launched through `supervise.sh`**, never `run-leaf.sh` or `claude` directly:
  stuck detection lives only there.
- **The verifier is blind by construction.** No input of `build-verify-prompt.sh` can carry the
  developer's rationale, so it cannot leak; every input is checked against that, and none may be
  added that could. The `refactor` phase takes `<base-sha>` instead of the test id (#151),
  exit 2 unless it matches `^[0-9a-f]{7,40}$`, so it can carry only a hex commit name; the
  verifier reads `git diff <base-sha>..HEAD`, not commit messages. `--branch-base <sha>`, the conductor's recorded
  branch base every phase takes (#4375), `diff` included (#4376), and `--step-green <sha>`, the step's own green tick only
  the `refactor` phase takes (#4544), are held to the same pattern. `verify-surround`, which judges a
  legacy step's characterization tests, is blind the same way: it takes the `pin` phase's inputs.
  `VERI_SKIP_VERIFY` (pinned per run, `plan` and `surround` never) skips the named verifiers
  (ADR-0033).
- **The committed ledger is the source of truth** for done steps; the issue only mirrors it.
  A step's green tick appends `⟂ refactor pending`, removed only by its verify-refactor PASS,
  so a resumed run can tell green from finished.
- **Eleven budgets on eleven axes, never merged**, one row each:

  | Knob | Axis | Default |
  |---|---|---|
  | `VERI_STUCK_RETRIES` | liveness: no answer | 1 |
  | `VERI_NO_VERDICT_RETRIES` | protocol compliance: finished without a `VERDICT:` line | 1 |
  | `REVISE_BUDGET` | verdict: rejected | 2 |
  | `VERI_REFACTOR_BUDGET` | cost: the transforms one refactor leaf may apply for the whole step (ADR-0017) | 5 |
  | `VERI_STEP_GROWTH_PERCENT` | plan growth: max `⟦added⟧` steps per ledger, as a percent of the steps in the verified plan, rounded up (ADR-0022) | 50 |
  | `VERI_SKILL_EDIT_BUDGET` | the attempts one `⟦skill-edit⟧` step's author may make | 3 |
  | `VERI_MISSING_REROUTE_BUDGET` | repeat missing reroutes per step: a missing test is not a rejected product, so `REVISE_BUDGET` would bail correct code | 3 |
  | `VERI_ADJUDICATE_BUDGET` | exit-2 judgments per run; 0 keeps today's behaviour | 2 |
  | `VERI_CI_FLAKE_RERUNS` | CI re-runs of a red head per run: a flaky CI job is not a defect; 0 keeps today's behaviour | 1 |
  | `VERI_TEST_QUALITY_FIXES` | cost: the test-quality steps one run may add: a weak test is not a rejected product | 1 |
  | `VERI_SURROUND_MUTANTS` | the mutants a legacy region owes: a missing mutant is not a rejected product | 5 |

  One knob over any two would make different failures one decision (ADR-0020). A bad
  `VERI_REFACTOR_BUDGET` is caught in preflight.
- **The developer's and the verifier's models are separate knobs**: `VERI_MODEL` (every leaf),
  `VERI_MODEL_DEVELOPER` (`develop-*`, `revise-*`), `VERI_MODEL_REVISE` (redo leaves:
  `revise-*`, `develop-exhausted`), `VERI_MODEL_REVISE_GREEN` (`revise-green` only, so it beats
  `VERI_MODEL_REVISE` there), `VERI_MODEL_VERIFIER` (`verify-*`),
  `VERI_MODEL_ADJUDICATOR` (the `adjudicate` leaf; unset, it runs on opus) and
  `VERI_MODEL_CONDUCTOR` (the conductor); the narrower one wins. Unset, first-try developers
  and verifiers run on sonnet, redo leaves and the conductor on opus (an empty
  `VERI_MODEL_CONDUCTOR` counts as unset). A weaker verifier shows as a changed verdict
  distribution, a weaker developer as more revise cycles; one knob would hide which.
- **Selection is four bands, one sort key.** `solvable-issues.sh` lists `priority` `bug`s first,
  then the other `priority`-labelled issues (`VERI_PRIORITY_LABEL`; set-but-empty is exit 2), then `bug`s, then the rest,
  each band ascending by number. A `low-risk` bug counts as the rest, and `priority` outranks `low-risk`.
  An issue also inherits the band of every open issue that names it under `## Blocked by`,
  transitively, taking the better of its own band and the inherited one: blocking a `priority`
  `bug` puts it in the first band, blocking another `priority` issue in the second, and blocking
  a plain `bug` lifts nothing. The bands only reorder the solvable set, never enlarge it,
  inherited bands included: open, opted in (`VERI_LABEL`), written by an `OWNER`, `MEMBER` or `COLLABORATOR` or
  labelled `VERI_AUTHOR_LABEL` (default `author-read`) once read, unblocked and unclaimed filter first,
  so neither `priority` nor blocking a `priority` issue makes an issue takeable.
- **Refactor-owed items are issues titled `Refactor candidates left by #<n>`**, labelled `refactor`
  and `refactor-owed` and never opted in (no `VERI_LABEL`), so selection never takes them;
  `/vgroom --refactor-owed` reads them.
- **An issue labelled `legacy` is the legacy kind**, never also `refactor` (capture refuses both,
  exit 2): it runs Seam → Surround → Verify under `skills/tdd/LEGACY.md`, wrapping a region in
  black-box tests driven through a seam before any refactor touches it.

## Testing idiom

Every suite is pytest, under `skills/tdd/scripts/tests/py/`; `make test` and `make unit` each run
one `pytest` invocation, and nothing under `tests/` ends in `.test.sh`. pytest's own exit code is
trusted: 0 only when every collected test passed, 5 when none were collected. The autouse
`hermetic_environment` fixture in `tests/py/conftest.py` makes a case hermetic from ambient `VERI_*`.
It also sets `VERI_EVENT_STRICT=1`, so a case that writes an event `veri/event_table.py` does not allow
(an undeclared name or key, a missing required key, a value that breaks its key's declared format, or an empty value where none is allowed) gets exit 2 from `event.sh`/`event.mark`; a run's conductor never carries it.
`make test TESTS="<pytest file or node id> …"` runs only those, in the same one invocation.

**`skills/tdd/scripts/tests/py/unit/` is the fast tier**, run by `make unit` and by `make test`.
Admission bar: about 100 ms per case, no git, network, servers, real waits (`sleep`), nested
suites, or script run as a subprocess.

**`make unit` and `make test` run pytest** over `skills/tdd/scripts/tests/py/`
(`make unit`: `tests/py/unit/` only), launched by `skills/tdd/scripts/tests/leg/pytest_leg.py` on
`$VERI_VENV/bin/python3` (default `~/.veri-tools/venv`, from `make install-dev`; else PATH's
`python3`). The leg and its plugins under `tests/leg/` are production, not test files, for every check that splits
a change into the two (`case_reader.is_test_path`: the production freeze, the red-leaf restore, the transform
freeze), in veri's own tree only (#4262). Admission rule: no process but the interpreter. Each case times out at 30 s
(`VERI_PYTEST_TIMEOUT`, `@pytest.mark.timeout(n)`), a `process` case, or a `tree_audit` case, with no `timeout` mark of its own at 90 s
(`PROCESS_CASE_TIMEOUT` in `tests/py/conftest.py`), since load stretches a real process and a tree audit's cost scales with the whole tree; an explicit mark wins; a wait inside a case bounds itself below `VERI_PYTEST_TIMEOUT` (30 s by default), or its failure path is unreachable because pytest-timeout fires first.

The pytest leg's internals, the workers budget T, the core wait, leg registration, the bytecode cache, the full-run lock, the idle window and its refusals, are stated in [`skills/tdd/scripts/tests/py/README.md`](skills/tdd/scripts/tests/py/README.md), *The pytest leg*.

**Pytest case sizes** (#1259, #1513): an unmarked case is small — `git` and `python3` refuse
on its PATH (save `python3` on a `veri/` module). A case that starts a real process carries
`@pytest.mark.process("<boundary>")`; one that lists a repo directory outside its `tmp_path`
carries `@pytest.mark.tree_audit("<what it sweeps>")`. Collection refuses either without an
argument, and any unregistered mark. `make unit` deselects both; `make test` runs all. `gh`
and `curl` always refuse. Drive a ported script's CLI in-process with the
`run_cli(module, argv, stdin="", env=None, cwd=None)` fixture, which returns
`(code, stdout, stderr)`.

**A script ported to Python follows one convention; `status.sh` is the worked example**
(#634): its logic is a module of `skills/tdd/scripts/veri/`, and its `.sh` entry point a
`/bin/sh` shim that `exec`s `python3` on it — `$VERI_VENV/bin/python3` (default
`~/.veri-tools/venv/bin/python3`) when it meets the 3.12 floor (`VENV_FLOOR`), else the `python3` on PATH
when that does, else exit 2 naming each interpreter tried, its source and its version — holding no Python
source (no heredoc, no `python3 -c`). Its tests live in `tests/py/unit/test_<module>.py` (`tests/py/test_<module>.py`
when the guard names it), faking only process boundaries; its entry-point contract cases sit in
`tests/py/test_<module>_process.py`.

Per step, the red and refactor leaves run the test files covering the files the step changed, as
`affected-suites.sh` prints them, with the `veri: one test file:` command (`make test TESTS="<those paths>"` here):
the `changed` tier. `develop-green`, verify-green, verify-refactor, the transform verifier and the diff phase's leaf and verifier run the
fast tier plus that `changed` run; a revise leaf runs the tiers of the phase it redoes. No leaf or verifier runs more
than the fast tier plus the `changed` run (the `affected` tier is gone), save the rebased-tip leaves
(`develop-rebase`, `develop-reconcile`, `verify-rebase`) and the suite-repair verifier, which run the full suite.
`affected-suites.sh` never widens: a changed file no rule places adds nothing and is named on stderr, left to the
full suite. A changed `veri/<m>.py` (or `tests/leg/<m>.py`, or its `<m>.sh` shim, `-` read as `_`) lists
`tests/py/test_<m>.py`, `unit/test_<m>.py` and `tests/py/test_<m>_process.py` where they exist, and every `tests/py/test_*_process.py`
that imports or runs it by name (`veri.<m>`, `<m>.py`, `<m>.sh`, or the name of any shim whose `exec` line names `veri/<m>.py`, as a whole word), so a process file needs no name map;
when no process file names it, it lists those naming a module that imports it directly, one hop and no further (#4425).
Each run goes through `timed-test-run.sh`, which saves the whole output under the worktree's
`.tdd/test-runs/` and never hands a leaf the runner's raw stream. A project that declares `veri: quiet test files:`
gets that command, over the paths, as the `changed` run's command, its output reaching the leaf unchanged (its exit 2
reported as a broken run, never a test failure); without the line the leaf gets the exit code, at most the last 20
lines and the saved file's path. veri's own tree keeps `make test TESTS="<those paths>"`, since its leg needs make's
offline environment, and a bounded report: the counts, at most 10 failing cases each with its first failure line,
how many it cut, and the saved file's path; its own quiet line is what `detect-test-command.sh` and `/vinstall` read.
`make test`, the
**full suite**, runs once per PR before the PR is readied, again per repair step a red result
appends (#539), and on the rebased tip if the Draft PR step rebased (#1026) — unless
`rebased-tip-suite.sh` prints `ci`, the default where a workflow triggers on pull requests, which
leaves that tip's run to CI. Where `branch-suite.sh` prints `ci`, by the same default, the run before
readying is not made either: CI's run on the readied PR is the PR's full suite, and a red one gets
the one `⟦ci-repair⟧` step.

Tests inject rather than wait on a real model or clock: `CLAUDE_BIN` swaps in a stub,
`VERI_HEARTBEAT` / `VERI_TOOL_IDLE` / `VERI_TIMEOUT` / `VERI_STUCK_RETRIES` shrink the supervisor's windows,
`VERI_FETCH_RETRY_SLEEP` the ref-lock retry — hence every tunable is read as `${VAR:-default}`.

**A suite asserts behaviour** — outputs, exit codes, files, events; never process counts,
fork counts or timings (observe those with `make profile`, report them in the PR body).
**No suite runs another suite.** When a call count is
the behaviour, the code calls one wrapper and the test swaps in an in-process spy, never a
PATH shim counting processes.

A guard or failure path never watched to fail is not tested: break it, see it go red, restore.

## Graded prose

A `GRADED` file holds one line per graded unit, its fields split on a single space: the unit
path, the signature, the date, the grading id and the grader-template prefix. `grade-prose.sh`
writes the line when a grade PASSes; it is never written by hand. Since the fields are split on
single spaces, a heading unit's field writes each `%` as `%25` and each space as `%20`, and every
reader decodes it.

The signature is a sha256 over the unit's text, its requirement rows and the grader model (plus
the grader's effort level when `skills/tdd/grader.conf` sets one), so a change to any of them
makes the unit owe a grade, however unrelated the edit looks.

A unit's rows live in the `REQUIREMENTS.md` beside its `GRADED` file, under a heading naming the
unit (`## <unit path>`). A unit under `skills/<x>/` is signed in `skills/<x>/GRADED`; any other
unit in its own directory's `GRADED`.

A unit may be one section of a file, a heading unit named `<file>#<heading>`, with its rows under
`## <file>#<heading>` in the `REQUIREMENTS.md` beside the file. Its text is its own text: its
heading line and the lines after it, up to the next unfenced heading line of any level, so its
subsections are not in it. Once any tracked `REQUIREMENTS.md` lists a heading unit of a file, that
file's whole-file unit is split: it is shown to the grader and signed over its view instead of the
file's text. The view is the file's heading lines in order, then the text above the first heading
and the own text of every section no heading unit claims. So an edit inside a claimed section owes
only that section's unit, and an edit to a heading line still owes the whole-file unit.

`prose-owed.sh`, run by `make unit` and `make test`, exits 1 listing each unit that owes a grade
and each orphan `GRADED` line (one whose unit has no rows any more). It also lists, ending
` (no rows)`, each `.md` file under `skills/tdd/scripts/prompts/`, `REQUIREMENTS.md` excepted, that no
`REQUIREMENTS.md` lists as a unit, so a prompt file cannot land without rows. A `⟦skill-edit⟧` step
regrades a unit.
