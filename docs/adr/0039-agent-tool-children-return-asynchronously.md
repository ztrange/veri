# Agent-tool children return asynchronously

A child the Agent tool launches may return asynchronously: the launch answers "Async agent launched
successfully" and the child's result arrives later as a notice, with no background flag set and no
foreground mode to ask for. A subagent whose turn ends while such a child runs is never woken by
the child's completion (a top-level session is: the completion notice starts its next turn). So `skills/vish/SKILL.md` (`## Who does what`, VSH31) has the main
thread wait inside its turn, on a blocking watch with its own timeout, after every launch. This
records a property of the Claude Code harness, not of code in this repository; it narrows ADR-0001,
whose "the parent only waits" assumed a child that blocks the parent's turn.

## Context

On 2026-11-26 the vish lanes for #4759 and #4760, each itself a background Agent of a `/vdev`
session, ended their turns on a "waiting for the report" line and were never resumed. Every child
launch in both transcripts (#4759: 1, #4760: 10) returned asynchronously, so the rule then in
`## Who does what`, "every child runs in the foreground", could not be obeyed. #4760 survived 9
children by staying in its turn on a `Monitor` watch for the child's commit, and died on the 10th
when it ended the turn instead (#4793).

## Consequences

A brief for an agent that starts children says how it waits for them: a `Monitor` until-loop or an
equivalent watch on the child's result notice, its commit or its output file, with a timeout. The
`claude -p` leaves the conductor runs (ADR-0001) are unaffected: `supervise.sh` owns their lifecycle.
