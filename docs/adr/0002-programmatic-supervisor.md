# Launch every leaf through a programmatic supervisor

Every `claude -p` leaf is launched through a supervisor script — never directly. The
supervisor spawns the leaf in the background, watches its heartbeat (progress-log
activity) plus a hard timeout, and kills + retries/escalates a leaf that hangs or goes
silent. Robustness against stuck or distracted leaves is treated as a first-class,
non-negotiable property of the framework, present from the first issue solved.

## Context

The user initially leaned toward "pure subprocesses + helper scripts, add supervision
later," but on reflection chose to build the supervisor immediately: not getting stuck
is the whole point of an unattended TDD worker, and a blunt inline `timeout` can't tell
"slow but working" from "hung." The supervisor's heartbeat check makes that distinction.

## Consequences

A monitoring layer exists before the first issue is solved — accepted cost. The
conductor never calls `claude -p` directly; it always goes through the supervisor, which
owns timeouts, kill, retry budget, and escalation. This is the single choke point where
stuck-detection policy lives and can evolve.
