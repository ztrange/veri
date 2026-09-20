# A test framework is priced per example, and veri's tests are mostly examples

veri keeps its hand-rolled plain-shell suites. ShellSpec 0.28.1 was vendored and three real
suites were ported to it faithfully — one from each shape veri's suites take — then measured
against their originals under the Makefile's own environment. It is slower on every shape,
smaller on none, and it cannot express three things the existing suites do today. The
ergonomics it was wanted for are real; they are not worth what it charges for them.

The spike itself — the vendored tree, the three ported suites and the raw measurement — is
[PR #374](https://github.com/ztrange/veri/pull/374), closed unmerged on purpose. None of it
belongs on `main`; 87% of that diff is a library this ADR declines to adopt. The PR is the
durable record, and GitHub keeps a closed PR's diff.

## Context

The question came out of the PRD-003 thread: mocks and spies read better in a framework than
in hand-rolled bash, agents know bats and ShellSpec well so new tests would come out more
uniform, and one standard shape is easier to read than eighty-nine home-grown ones. All three
are true. The spike existed to price them.

ShellSpec was the candidate rather than bats-core because it is pure POSIX shell (so it can be
vendored, and CLAUDE.md commits the testing idiom to zero dependencies) and is designed to be
lighter than bats, which is known to be fork-heavy.

Three suites were ported, chosen to span the shapes:

| Suite | Shape | Why it was picked |
|---|---|---|
| `tests/unit/push-branch.test.sh` | fast tier: script sourced, dependencies mocked as shell functions, no process started | the best case for a framework, and the tier #336/#341 built |
| `tests/skill-refactor-pending.test.sh` | prose: reads SKILL.md and the prompts as text | the worst fit, and the shape ~23 suites have |
| `tests/issue-worktree.test.sh` | heavy integration: a real git repository per case, script run as a process | the shape most suites have, and where the time actually goes |

Every case was ported, not a sample, and every ported case was proven still to assert by
planting a bug and watching it go red — 4/4, 59/60 and 25/25. That proof is the expensive part
of any migration and the reason a bulk rewrite was never on the table: a migrated case that
quietly stops asserting still passes, and tests have no tests.

## Considered options

- **ShellSpec** — measured below.
- **bats-core** — not measured. It charges on the same axis and more: a subshell per test plus
  helper processes, and `bats-mock` stubs commands through PATH, which is the executable-per-
  mock shape that costs ShellSpec the most here. Its TAP output needs the same custom-formatter
  work. If ShellSpec loses on cost, bats loses harder.
- **shunit2** — the lightest: one sourced file, no per-test process. It also offers the least —
  no mocking and no per-test isolation, and per-test isolation is the one thing ShellSpec gave
  for free.
- **A ~50-line in-repo helper** — `it "name" fn` with a subshell per case and named assertions.
  Gives the ergonomics with no dependency, no new failure modes, and no per-example toll.

## Decision

Do not adopt a test framework. Keep the plain-shell idiom CLAUDE.md describes.

If the ergonomics are wanted — and the spike agrees they are worth something — take them from
the in-repo helper, not a dependency. That is a separate, much smaller piece of work.

## Consequences

**It is slower on every shape.** Median of three runs each, both sides under the Makefile's own
offline environment, on the development Mac, **measured at `f04cf4c9`** — where the suites were
85 in `tests/` plus 6 in `tests/unit/`. The anchor matters: this repository moved 446 commits in
the two days the spike took, so a figure with no commit beside it is a figure that rots.

| Suite | Hand-rolled | ShellSpec | |
|---|---|---|---|
| `unit/push-branch` (4 cases) | 0.11 s | 1.03 s | **9.4×** |
| `skill-refactor-pending` (7 cases, 62 probes) | 0.28 s | 1.40 s | **5.0×** |
| `issue-worktree` (25 cases) | 7.60 s | 10.03 s | **1.3×** |

The ratio falls as a suite gets slower because the charge is roughly constant per example —
about 0.1 s. That is the finding, not the ratios:

- **The fast tier's admission bar is about 100 ms per case.** ShellSpec's own per-example
  overhead is about 100 ms. A unit case would spend its entire budget on the framework before
  running a line of its own. The tier a framework would help most is the one it cannot enter.
- **The charge is worse here than the numbers say.** `Mock foo` creates both a shell function
  (so in-shell calls cost no process — the framework is not naive about this) *and* an
  executable file `foo` in a per-example temp directory placed on PATH, so child processes see
  it too. ShellSpec also writes stdout, stderr and leak capture files per example. A fresh temp
  directory per run means those executables are never-before-seen every run, which is exactly
  the ~330 ms macOS first-run check CLAUDE.md documents under "the first run of a new
  executable" — and CLAUDE.md also records that a Claude desktop session is never covered by
  the developer-mode exemption. The framework's per-example cost lands hardest in the
  environment veri actually runs in.

**Three things the existing suites do that it cannot.**

1. **A faithful port cannot be green.** Two integration cases assert nothing about stdout on
   purpose — their subject is the commit the worktree lands on. ShellSpec WARNs on unread
   stdout, `--warning-as-failure` is on by default, and it is a global CLI flag with no
   per-example override (`lib/core/dsl.sh:269` reads one global). The choice is to add
   assertions the original does not make, to run those two red, or to disable the warning for
   every example in every suite — which switches off a real check (a subject exiting non-zero
   with nothing asserting on it) everywhere, to accommodate two cases.
2. **A claim asked in two places cannot be factored into one helper.** `The` and `Assert` are
   refused outside an Example. The prose suite factors three such claims deliberately —
   `precedes`, `says_exit_codes`, `says_pending_until_verified` — and their comments say why:
   two call sites that must stay identical. The port had to duplicate all three verbatim at
   both call sites, reintroducing exactly the drift the helpers exist to prevent.
3. **One `When` per example.** Five of the 25 integration cases invoke the script twice. Only
   one invocation can be the watched subject; the other becomes ordinary shell in the body.
   For the case covering `--remove` against a clean and then a dirty worktree, it is the
   destructive half that goes untraced.

**And three smaller frictions.** ShellSpec turns errexit on inside an example, so the repo's
`set -uo pipefail` idiom of assigning from a `git symbolic-ref` that is absent by construction
aborts the example before its `When`, reported only as "Example aborted (exit status: 1)" with
no line number. There is no regex matcher in 0.28.1 — `match pattern` is glob — so all 62 of
the prose suite's EREs stay hand-written predicates and the framework contributes only the
invocation. And an example shares one subshell across its `Before`, `When`, every `The` and its
`After`, so a `PATH` set inside a case leaks into its own later assertions; the hand-rolled
suite's literal `( … )` scoped that more narrowly for free.

**It is not smaller.** Counting non-comment, non-blank lines: 119 vs 120 for the unit suite,
304 vs 307 for the prose suite, and **499 vs 417** for the integration suite — the port is
larger where it matters most.

**Age is not the reason, and no newer version helps.** 0.28.1 is from January 2021. The project
is not archived and its default branch still takes commits, but those commits are portability
work for old and exotic shells. The one outright bug the spike hit — `When run command` with an
absolute path fails 127, because `shellspec_which` (`lib/general.sh:586`) is a PATH walk with no
absolute-path case — is byte-identical on the default branch today, four years on. Everything
else above is design, not rot. Vendoring would have frozen a tree with no dependencies, no
network and no privileged operations, so the usual costs of running old code barely applied;
the cost of age here is only that veri would own the bugs, and the spike found one it would
have had to work around.

**What was genuinely better, and is worth stealing.** A subshell per example makes state
leaking between cases structurally impossible, where the hand-rolled suites depend on every
case remembering to reset. Failures carry the `file:line` of the failing expectation rather
than only the case name, and show got-versus-expected per assertion instead of a hand-written
failure string that has to re-spell every probe — one such string in the prose suite is a
single 600-character line, and a failure message naming a probe the assertion no longer makes
is a real drift risk. A single case can be re-run by `file:line` instead of re-running fifteen
seconds of suite. Those four are the shopping list for the in-repo helper; the first is most of
its value.

**The count line was solvable, cheaply.** `make test` does not trust a suite's exit code (#157)
and greps its last line for `^[0-9]+ passed, [0-9]+ failed$`; ShellSpec ends a run with
"N examples, M failures" and two newlines. A custom ShellSpec formatter prints veri's line
instead, at no process cost. Two things it taught, which outlive the spike: a WARNED example
makes ShellSpec exit non-zero while counting in neither `failed_count` nor `error_count`, so a
naive count line reports a red run as green; and whether a warning is a failure is a CLI flag,
so a count line that hard-codes either answer lies in one configuration. Both are the failure
#157 exists to catch, found by planting the case rather than by reading the code. The
structural mismatch left over: the guard is per-suite, and ShellSpec's unit is one process per
run, so adopting it would have meant deciding where that guard goes.

**A hole in an existing suite, found on the way** — filed as
[#411](https://github.com/ztrange/veri/issues/411). The `entry_says
'strip|remove|drop|clear|delete'` probe in `skill-refactor-pending.test.sh` (line 619 when the
spike found it, 677 nine commits later — cited by pattern because the line moves) asks whether
the `clear-refactor-pending.sh` entry says one of those verbs. The
entry it reads opens with the words `clear-refactor-pending.sh`, so the alternation is
satisfied by the filename whatever the prose says. That probe cannot fail. It is a pre-existing
hole, carried over faithfully by the port and confirmed against the original — not a port
defect, and worth its own issue.
