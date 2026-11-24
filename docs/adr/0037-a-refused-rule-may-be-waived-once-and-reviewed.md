# A refused rule may be waived once and reviewed

A bail caused by a whitelisted process rule is first sent to the adjudicator (ADR-0035), which may
now answer `deviate`. The run then takes that rule's resume action instead of bailing, at most
`VERI_DEVIATION_BUDGET` times per run (default 1). Each deviation is recorded as a `deviated` event
and an unticked ⟦human-owed⟧ ledger line, which `/vmerge` reviews before the merge. This extends
ADR-0035: the adjudicator still writes nothing, and a deviation it did not grant is the same bail as
before.

## Context

Measured on 2026-11-23 at `da06a64ac0` (`specs/prd-043.md`, *Facts*): of a sample of 14 of the
42 `revise-impossible` and `needs-user` bails since 2026-11-09, 7 were a rule blocking correct work.
Each such bail costs a human resume or a re-plan, and the work lands a day later.
`graded-edit-outside-skill-edit` bails directly, at the green and refactor sites of `SKILL.md`.

## Decision

- **D1: judged at the bail.** A new first sub-step of `skills/tdd/BAIL.md` sends a bail whose
  cause a whitelisted rule names to the adjudicator. A bail on any other cause is unchanged.
- **D2: the rule's own resume action, for the refusing step only.** Each whitelist entry states
  it once. The run writes a ⟦human-owed⟧ ledger line naming the rule ID, the adjudicator's
  one-line reason and the action taken. For the graded-prose fence the action is a reroute, not a
  skip: the step's commit stays and one `⟦skill-edit⟧` step regrades the changed units.
- **D3: the review verdict lives in the committed ledger.** On OK, `/vmerge` ticks the line with
  `⟦reviewed ok⟧` appended, commits it on the PR branch before the merge, and updates the PR body
  to match. NOT OK goes to the human as an issue comment, and nothing merges. There is no
  `deviation-reviewed` event: `events.jsonl` lives in the run's worktree, which may be gone by
  merge time.
- **D4: a budget of its own.** `VERI_DEVIATION_BUDGET`, default 1 per run, is the thirteenth
  budget (ADR-0020): a deviation is not a no-answer, a rejection or a missing verdict. The
  adjudication that grants it still spends `VERI_ADJUDICATE_BUDGET`. Either one spent means a
  plain bail, and every `deviated` event of the issue counts, so a resume does not refresh it.
- **D5: a whitelist, read by a script.** `ADJUDICATE.md`'s *Waivable rules* lists, in 043.1,
  only `graded-edit` (`graded-edit-outside-skill-edit`). The test freeze and verify-pin's
  fail-at-base requirement follow in PRD 043.2 and 043.3. A rule absent from the list is never
  waived, whatever the adjudicator answers: `adjudicate.sh record` reads `deviate` for any other
  cause as unparsed. Never waivable: the blind verifier's inputs, a verify-green or
  verify-refactor REJECT of production code, exit-code semantics, `supervise.sh`, the committed
  ledger, the skill snapshot pin, a missing or obsolete target, and a real spec gap.

## Considered options

- **Waiving at the refusing check**: rejected. Each check would need its own adjudication call and
  its own prose, the special case per incident ADR-0035 set out to end; judging at the bail
  keeps one site.
- **An automatic pruning report** that retires a rule once its deviations keep being reviewed OK:
  rejected. Which rules to prune is the human's call, made by reading the recorded deviations and
  their verdicts; no automation makes it.
