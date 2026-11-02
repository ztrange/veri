# The first-try developer stays on Sonnet, not Haiku

First-try developer leaves (`develop-*`) keep running on Sonnet (`VERI_MODEL_DEVELOPER`
unset, or `sonnet`), even though Haiku did the same work for about a third of the price in a
trial. The veri workflow is now tuned well enough that slower development is not worth a small
saving.

## Context

Trial, 2026-11-01 → 2026-11-02: three runs launched with `VERI_MODEL_DEVELOPER=haiku`,
`VERI_MODEL_REVISE=opus`, `VERI_MODEL_VERIFIER=sonnet` and the conductor on Opus: #2875 (merged
v0.962), #2878 (merged v0.968) and #2825 (all steps verified, but #2901 had already solved it).
The blind verifier gated every Haiku step. Neither review raised a Haiku-specific concern, and
no bail was Haiku's fault.

| | Haiku trial (3 runs, 16 steps) | Baseline (30 runs before it, 124 steps) |
|---|---:|---:|
| whole run, $ per step | 1.14 | 1.28 |
| first-try developer, $ per step | 0.063 | 0.188 (Sonnet) |
| first-try developer, turns per step | ~32 | ~10 |

The saving is about 10% of a run's cost, because the Opus conductor is 60–80% of the bill.
Haiku took about three times as many turns per step, so each step was slower.

## Considered options

- **Haiku as the default developer**: rejected. It saves about $0.13 per step but makes
  development slower, and three runs cannot rule out more rework.
- **Haiku on some leaf kinds only**: not pursued, for the same reason.

## Consequences

- The knob stays: `VERI_MODEL_DEVELOPER=haiku` still works for a one-off run.
- Cost work goes after the conductor first, since that is where most of the money goes.
- Revisit this decision if Haiku gets faster, Sonnet's price rises, or a larger sample shows a
  bigger saving.
