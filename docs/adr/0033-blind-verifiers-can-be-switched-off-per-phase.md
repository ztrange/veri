# Blind verifiers can be switched off, phase by phase

Blind verification ([ADR-0003](0003-blind-independent-verifier.md)) stays on by default. An
operator may switch it off per phase for one run, using `VERI_SKIP_VERIFY=<phase>[,<phase>…]`
with phases `red`, `pin`, `green`, `refactor` and `diff`. verify-plan can never be switched off.
This amends ADR-0003, which states blindness without exception.

## Context

Measured on 2026-11-05 at `76e8efb24b`, over the 30 latest committed metrics reports:

- Verifier leaves cost $31.86 of $242.32, which is 13.1% of run spend, conductor included.
- They answered REJECT 62 times in 354 attempts (17.5%).

The checking is worth paying for by default. Some runs (an experiment, an issue being re-run, a
cost-capped night) are better off trading it away, and there was no way to do that.

## Decision

- **One list, one phase per word.** Phases differ in cost and in what they catch. A single
  on/off switch would hide which one was traded.
- **`plan` is refused.** verify-plan is the cheapest verifier and the only check of the plan
  against the issue. `criterion-finished.sh` ticks criteria from the plan's own wording, so an
  unverified plan would let the run grade itself.
- **Skipped is recorded, never passed off as PASS.** A skipped phase writes the
  `verify-<phase>-skipped reason=switched-off` event and `skipped` in its verdict exit file. The
  run then continues as after a PASS.
- **Pinned per run.** The list is written to `.tdd/issue-<n>-skip-verify` and survives resumes.
  Only `VERI_NEW_SKILL=1` re-pins it, the same rule as the skill commit.
- **From the environment only.** A label would let anyone who can label an issue switch
  verification off.
- **Visible, not blocking.** The PR body and the ✅ Done comment carry
  `⚠️ Unverified phases: …`, and metrics count the skips. Merging is not gated.

## Considered options

- **One on/off switch**: rejected, since it hides which phase was traded.
- **Allowing `plan` to be skipped**: rejected, for the reason above.
- **A label per issue**: rejected, for the reason above.
- **Gating `/vmerge` on unverified phases**: rejected. The operator chose the trade, and a gate
  would only make them merge around it.

## Consequences

- Each phase lands separately (PRD 018.1–018.4, refactor first), because each is coupled to
  different machinery.
- A run whose verify-green is skipped loses the `wrong-test-route.sh` reroutes, since they are
  verify-green REJECT outcomes.
- Mechanical checks that are not verifier leaves keep running: `pin-recheck.sh` and the full
  suite. Whether `mutation-parity.sh` keeps running is decided in 018.2 (recommended: yes).
