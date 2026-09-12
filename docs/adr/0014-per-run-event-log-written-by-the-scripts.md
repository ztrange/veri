# Observability is a per-run event log written by the scripts, not a service

A run records what happened to an append-only event log in its worktree, one line per
event with a timestamp: the supervisor writes every leaf launch, attempt and exit (with
the kill cause), the verifier writes the verdict, a harvester reads each leaf's own
closing usage record for wall time, turns, tokens and dollars, and the conductor marks
only what it alone knows — step start, step done, pin, bail, completion — through one
small script the procedure tells it to call. Every viewer (the terminal status, the local
web dashboard) and every metric (per-issue summary committed beside the ledger and posted
with the final comment; per-scope totals shown but never committed) is a **reader** of
that log. Nothing runs in the background to collect it.

## Context

Until now a run was observable only through the issue thread — prose, no clock, no cost —
and the supervisor's one-line status. Time and cost were already on disk in every leaf's
closing usage record, but nothing harvested them, and no file said when a phase began.

Rejected: **the issue thread alone**, because GitHub comments are a human record and
cannot carry the timing or the token counts a viewer needs at a glance. **A collector
daemon or hosted service**, because it is always-on infrastructure for a tool that runs a
few hours a day, and a dependency every foreign target repo would inherit. **Inferring
the conductor's state from the ledger and the comments**, because ticks and posts say
what settled, not when a phase began or how many attempts it took.

## Consequences

Leaf-level events are load-bearing and come from scripts, so they are complete; the
conductor's marks depend on prose being followed, so a reader tolerates a missing mark
rather than failing. Tokens and dollars are per leaf: a conductor's own usage is visible
only when it runs in print mode, and the metrics say which. The log is run state under
the `.tdd/*` ignore rule and disappears with the worktree; the committed markdown summary
is the durable record. Two words the metrics need are defined in the glossary and must not
be merged: **rework** (rejected attempts a step recovered from) and **waste** (everything a
bailed step spent, passing verdicts included).
