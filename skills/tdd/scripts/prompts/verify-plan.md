{{SHARED}}

## Phase: verify-plan

The conductor has scoped one issue into a plan — the ledger below — and is about to run its
steps. Your subject is that plan, not anyone's code.

### The issue's behavior spec

{{ISSUE_SPEC}}

### The proposed plan (the ledger)

{{LEDGER}}

### Your checks

1. **Every criterion is delivered by its steps, taken together.** For each acceptance
   criterion `k` in the spec, read the ledger steps tagged `⟦criterion k⟧` and ask one
   question: do those steps, together, deliver criterion k **as written**, in the
   criterion's own terms rather than the plan's paraphrase of it? A step naming some
   mechanism the criterion might be built from delivers the criterion only when that
   mechanism is sufficient for the criterion as written: a mechanism that is necessary but
   not enough leaves the criterion undelivered, however true the step is of the mechanism.

2. **Any step too big for one Red → Green → Refactor cycle.** Read each step on its own
   and ask whether a developer could take it from one failing test to green and then tidy
   up: a step bundling two or more new behaviours is too big for one Red → Green →
   Refactor cycle. This check carries no verdict of its own — name every step you judge
   that way in your `REASON:` line, whether the verdict is PASS or REJECT, so the
   observation reaches the conductor either way.

Use PASS when every criterion is delivered by the steps tagged for it; check 1 is the whole
of what the verdict asks, so a plan meeting it passes even where you would have planned the
work differently. REJECT the plan when no step establishes a criterion as written — an
uncovered criterion is itself the REJECT, not a PASS whose reason mentions the gap.

Two shapes of criterion have no failing test to write, so the plan carries each as one line
rather than a step:

- A criterion whose only observable is that the repository's test command passes — "the
  suites are green" — is one `⟦full-suite⟧ ⟦criterion k⟧` line, covered by the full-suite run.
- A criterion whose deliverable is the record of a manual check only a person can make is owed
  by a human, so it is one `⟦human-owed⟧ ⟦criterion k⟧` line that no developer leaf is ever
  handed. A go-red guard (a guard broken on purpose, watched going red, restored) is not that
  shape: an agent can do that check, and it is never marked `⟦human-owed⟧`.

For check 1, a `⟦full-suite⟧ ⟦criterion k⟧` or `⟦human-owed⟧ ⟦criterion k⟧` line delivers
criterion k by itself, except that a `⟦human-owed⟧` line on a go-red guard delivers nothing.
Such a criterion is owed no step, and its line is never a reason to REJECT.

REJECT a plan that turns either shape — the test command or the suites passing, or the record
of a manual check only a person can make — into a Red/Green step instead of its `⟦full-suite⟧`
or `⟦human-owed⟧` line, even where check 1 alone would pass it: a Red leaf handed that step can
only answer `UNTESTABLE`, and the run bails. Also REJECT a plan that marks a go-red guard step
`⟦human-owed⟧`: that leaves a check an agent can do waiting on a human.

REJECT a Red/Green step when a criterion of the issue forbids adding or changing tests, as in run #72: a refactor whose criterion says the test diff changes only one existing call, planned as a Red/Green step whose Red adds a case the diff phase must then delete, which verify-diff rejects on every revision; such a criterion is planned as a refactor or `⟦diff-checked⟧` step instead.

A go-red guard is one line, ``- [ ] <criterion>, probe `<file>` `<old>` → `<new>` on `<case>`
⟦go-red⟧ ⟦criterion k⟧``: the break (`<old>` replaced by `<new>` in `<file>`, none of them holding
a backtick, `<new>` possibly empty) and the existing case it must turn red. For check 1 such a line
delivers criterion k. REJECT a go-red guard planned as a Red/Green step instead of that line, and a
`⟦go-red⟧` line whose probe lacks that form: a Red leaf handed the guard can only answer
`UNTESTABLE`, and a line without the form stops the run before any probe.

A third shape has no test to leave behind: a diff-property criterion, one that is a property
of the branch's own diff — something removed, something left unchanged, a change confined to
named lines — is one `⟦diff-checked⟧ ⟦criterion k⟧` line, judged against the diff by a blind
verifier. A `⟦diff-checked⟧ ⟦criterion k⟧` line delivers criterion k by itself. A criterion
stating a rule every future change must keep is not this shape, and stays a Red/Green step.

REJECT a plan that turns a diff-property criterion into a Red/Green step instead of its
`⟦diff-checked⟧` line, and REJECT a plan with a step whose test reads another suite's source text
or the git history: such a test pins text rather than behaviour, and goes red on the next
legitimate edit of what it reads.

REJECT a plan that carries a Red/Green step whose criterion changes prose or prompt text: a change
to a unit with a requirements list is that unit's `⟦skill-edit⟧` step, and a change to text no list
claims is a `⟦diff-checked⟧` line, judged blind against the diff.

REJECT a plan with a step that changes what existing cases outside the changing step's own Red pin, without a step that updates those older cases ahead of the changing step. Each of these kinds counts: a script's output (a usage string, a constant, output compared verbatim or by checksum); the input those cases feed, made unacceptable; what a fake those cases use must return; and the calls, or their order, a fake records. Green may not edit a test, so the older cases go red and the revise budget runs out. Your reason names the changing step and what its older cases pin. The `### Test cases touching the files the plan names` section, after the ledger, lists the committed test cases touching the files the plan's steps name: their names, under each test file's path, never their bodies. Read those cases in the repository and apply this check to them: one that pins what a step changes is an older case that step needs updated ahead of it. A `<file>: cases not readable` line names a touching test file whose cases could not be listed; read it in the repository and apply the check to its cases too.

REJECT a plan with a step that introduces a branch — a fallback an existing suite forces in,
say — that only a later step's test requires: that step's blind green verifier sees code none
of its own tests requires, and rejects correct code until the revise budget runs out. Your
reason names both steps, the introducing step and the later pinning step, so the plan can be
reordered or the branch moved to the step that pins it. A step bringing in code after the
steps that pin its branches is not a REJECT on ordering grounds, and neither is one bringing in
only the branches its own test requires, the rest arriving with the steps that pin them.

REJECT a plan whose only steps for a criterion delivered by an interface change that also asks
for a test case are a `⟦phases: …⟧` step: the case must be its own Red/Green step tagged with
the same `⟦criterion k⟧`, because a case that exists only inside the phased step is never
checked by a verifier. Your reason names the criterion and the test case it asks for.

REJECT a plan whose step drops a constraint the issue attaches to the cases that step covers:
the case size it must keep (medium, with a real process), "no production change", or an
end-to-end path through real processes that must stay covered. Your reason names the step and
the constraint it leaves out.

REJECT a plan that plans a test-only change, one satisfiable only by editing a test, as a
Red/Green step: Green may not edit a test, so the run bails on it. Such a change is a pin step
when it adds a test case for behaviour that already holds: an ordinary step whose Red reports
that the case already passes (`AGAINST_UNMODIFIED: PASSES`). `⟦diff-checked⟧` is reserved for
steps that leave no test behind, so it is never offered for a change that adds a case.

REJECT a plan whose `⟦diff-checked⟧` step text asks for a test to be added (a case, a pinning case, a process case): verify-diff rejects every `⟦diff-checked⟧` step whose own commits add a test, so such a step can never pass. Your reason names the step and the test it asks for.

The exception is a well-formed `⟦fixture-repair⟧` step, for a defect in a test's own fixture,
stub or harness whose script under test is correct. Its line shape is `- [ ] <criterion>: repairs
the fixture '<fixture or stub name>' in <fixture file>, reproduced by a case in <test file>
⟦fixture-repair⟧ ⟦criterion k⟧`. REJECT a `⟦fixture-repair⟧` step whose spec places the defect in
the script under test, one that names no fixture (a function, stub or helper, not a line range),
and one whose fixture file is not a test file by `transform-touches-tests.sh`'s rule
(`case_reader.is_test_path`: `tests/` directories, `*.test.*`, JS/TS `*.spec.*`, Go `*_test.go`, and Python `test_*.py` or `*_test.py` anywhere). Your reason names the step and which of the three it is.

REJECT a plan in which a step's behaviour can only be observed once a later step is built: a
step asserting that an input is ignored, guarded or without effect ("even when X is left in
storage", "without dev tools") passes against unmodified code until a later step makes the code
read that input, so a test for it cannot fail first. Such a step belongs after the step that
makes the code read that input, and a plan placing it before the step that makes the code read
that input is the REJECT. Your REASON: line names both steps, the early step and the later step
it waits on.

REJECT a plan in which a step adds a script under `skills/tdd/scripts/` whose no-argument usage line and exit 2, or whose declared caller, arrives only in a later step, since the repo-wide audits go red on the adding step whatever its green does; your reason names both steps, the adding step and the later step that brings the usage or the caller.

REJECT a plan holding a step that carries the `⟦replaces-case⟧` mark but does not name its cases in the form `replaces '<case name>', '<case name>' in <suite path>`, quoting each case name: the guard that reads the names cannot read any other form, and your reason names the step.

REJECT a plan holding a step that carries `⟦guard-subject: P⟧` where the step text or the spec names `P` as that step's Red test file (the file its failing case is written in): `tests-frozen` records the Red's test file whole, so a Green editing `P` can never pass `tests-frozen check --step`; your reason names the step and `P`.

REJECT a plan with a step whose test asserts the wording of a unit with a requirements list, a unit some `REQUIREMENTS.md` has a `## <path>` heading for: a sentence, a phrase, or a checksum of its text or of a render that includes it. Your reason names the step and the unit. A test of a mechanical fact the unit states (a script it names, a heading a parser reads, a phase name the code accepts, a launch line run against a stub) is not a REJECT.

A **predicate step** is a Red/Green step whose criterion makes an outcome depend on a condition of the input or state ("when", "if", "only", "unless", a threshold), an output scoped to one caller or one outcome ("on <X>'s <outcome>", "only for <caller>") included, so the plan owes the counter-case in which another caller or outcome gets no such output; its **counter-case** is a step whose criterion states the outcome when that condition does not hold. REJECT a plan holding a predicate step whose next Red/Green step in the ledger is not its counter-case: one green alone fits the code to one side of the condition, and the counter-case right after it makes the second green generalise. Your reason names the predicate step and its condition. It is not a REJECT when an earlier step of the plan is the counter-case, or when a committed test case you find in the repository already pins the outcome when the condition does not hold. Only Red/Green steps count: a `⟦diff-checked⟧`, `⟦full-suite⟧`, `⟦human-owed⟧` or `⟦phases: …⟧` line is never a predicate step or a counter-case.

REJECT a plan in which a step's code dispatches on n outcomes (an exit code, a status, a kind) and no step tests the residual outcome no named branch takes, naming the step. REJECT, too, a plan in which a behaviour the issue or `SCRIPTS.md` states has no step that tests it, even when the plan tests a dispatch's residual outcome, naming the behaviour.

REJECT a plan that leaves to no step a site of a criterion's goal lying outside the files the criterion's check reads. A criterion's goal is what the criterion's own sentence, the issue's title and its `## Problem` say the change covers. When a criterion carries a runnable check, a command, that reads fewer files than the scope its goal names (one file where they name a directory, a package or every site), run the check's own pattern over that whole scope in the repository; a site that search finds outside the files the check reads, which no step of the plan changes, is the REJECT, since the check would then pass over an unfinished goal. Your reason names the criterion, the files its check reads, the scope its goal names and each site found outside those files, so that the rewritten plan can add a step covering them. It is not a REJECT when that search finds no site outside the files the check reads, or when a step of the plan, a gap step included, already covers each site found: a check narrower than its goal is never by itself the REJECT.

REJECT a plan holding a step whose text names more than one observable outcome: a behaviour plus each distinct refusal, exit code or fail-closed branch. The Red adds one case, so a second outcome is a guard no case pins, and verify-green rejects it until the revise budget runs out. Your reason names the step and the split it needs, one outcome per step. A step naming exactly one outcome, a behaviour alone or one guard alone, is accepted: count the named outcomes, and never refuse a step for merely mentioning a guard.

{{REFACTOR_PLAN}}

{{LEGACY_PLAN}}

A REJECT must name the criterion it fails on and state the part of it no step covers, in
the criterion's own words, so that the plan can be rewritten from your reason alone.

A step carrying no `⟦criterion k⟧` tag — a gap step, which the planning leaf is asked to
write for a behaviour the issue's prose needs and no acceptance criterion covers — is never
by itself a reason to REJECT: it belongs to no criterion, so check 1 has no question to ask
of it. It is still subject to check 2 like any other step.
