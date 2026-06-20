# Use `claude -p` subprocesses as the orchestration substrate

We orchestrate the TDD loop with `claude -p` leaf subprocesses driven by helper
scripts (the idiom from the `fc/my-skills` reference suite), rather than the Agent
tool or the Workflow tool. The decisive property is **control**: the parent owns each
subprocess's lifecycle, so a stuck or distracted leaf can be timed out, killed, and
inspected (via a `tail -f` progress log) without losing the whole run. The Agent tool
and Workflow give this up — when a nested agent hangs, the parent only waits.

## Considered options

- **Agent tool (subagents):** native, but a hung subagent blocks the parent, and
  subagents can't spawn their own agents — the independent verifier would force
  awkward contortions.
- **Skill → Workflow script:** deterministic loops/conditionals and trivial scaling
  to parallel, genuinely attractive — but the same loss-of-control on a hung agent,
  and more upfront machinery than the simplest-first path wants.
- **`claude -p` + helper scripts (chosen):** proven in the user's suite, strong
  permission-allowlist and forensic-logging story, and `claude -p` nests freely so
  developer and independent verifier are just sibling subprocesses.

## Consequences

`claude -p` nests without limit — flexible, but fan-out must be kept shallow and
bounded deliberately. Workflow remains a candidate for the v2 parallel rung if
deterministic fan-out outweighs the control property; the leaf skills are designed
substrate-agnostic so only the conductor would change.
