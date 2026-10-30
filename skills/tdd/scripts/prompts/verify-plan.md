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
- A criterion whose deliverable is the record of a manual check — each suite broken on
  purpose, watched going red, the output recorded — is owed by a human, not by code, so it is
  one `⟦human-owed⟧ ⟦criterion k⟧` line that no developer leaf is ever handed.

For check 1, a `⟦full-suite⟧ ⟦criterion k⟧` or `⟦human-owed⟧ ⟦criterion k⟧` line delivers
criterion k by itself: such a criterion is owed no step, and its line is never a reason to REJECT.

REJECT a plan that turns either shape — the test command or the suites passing, or the record
of a manual check — into a Red/Green step instead of its `⟦full-suite⟧` or `⟦human-owed⟧`
line, even where check 1 alone would pass it: a Red leaf handed that step can only answer
`UNTESTABLE`, and the run bails.

A third shape has no test to leave behind: a diff-property criterion, one that is a property
of the branch's own diff — something removed, something left unchanged, a change confined to
named lines — is one `⟦diff-checked⟧ ⟦criterion k⟧` line, judged against the diff by a blind
verifier. A `⟦diff-checked⟧ ⟦criterion k⟧` line delivers criterion k by itself. A criterion
stating a rule every future change must keep is not this shape, and stays a Red/Green step.

REJECT a plan that turns a diff-property criterion into a Red/Green step instead of its
`⟦diff-checked⟧` line, and REJECT a plan with a step whose test reads another suite's source text
or the git history: such a test pins text rather than behaviour, and goes red on the next
legitimate edit of what it reads.

REJECT a plan that carries a Red/Green or `⟦diff-checked⟧` step whose criterion changes prose or rendered prompt text, instead of a `⟦skill-edit⟧` step for its unit: a graded unit changes only through that step.

REJECT a plan that changes a script's output which existing cases outside the changing step's own Red pin (a usage string, a constant) without a step that updates those older cases ahead of the step that changes it: Green may not edit a test, so the older cases go red and the revise budget runs out. Your reason names the changing step and the output its older cases pin.

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
and one whose fixture file is not a test file by `transform-touches-tests.sh`'s rule (under a
`tests/` directory, or named `*.test.*`). Your reason names the step and which of the three it is.

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

REJECT a plan holding a step whose text names more than one observable outcome: a behaviour plus each distinct refusal, exit code or fail-closed branch. The Red adds one case, so a second outcome is a guard no case pins, and verify-green rejects it until the revise budget runs out. Your reason names the step and the split it needs, one outcome per step. A step naming exactly one outcome, a behaviour alone or one guard alone, is accepted: count the named outcomes, and never refuse a step for merely mentioning a guard.

{{REFACTOR_PLAN}}

A REJECT must name the criterion it fails on and state the part of it no step covers, in
the criterion's own words, so that the plan can be rewritten from your reason alone.

A step carrying no `⟦criterion k⟧` tag — a gap step, which the planning leaf is asked to
write for a behaviour the issue's prose needs and no acceptance criterion covers — is never
by itself a reason to REJECT: it belongs to no criterion, so check 1 has no question to ask
of it. It is still subject to check 2 like any other step.
