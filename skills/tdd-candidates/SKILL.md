---
name: tdd-candidates
description: >-
  Turn the candidates of an architecture analysis into GitHub issues veri can take.
  Invoke as `/tdd-candidates`. Use when an analysis has just listed candidates and the user
  wants them filed as a queue.
---

# tdd-candidates — file an analysis's candidates as veri issues

You shape and file the candidates an architecture analysis has already produced, one GitHub
issue per module, on the repository this session was invoked in. You do not survey the
codebase, you do not rank the candidates, and you do not judge whether any of them is worth
doing: that was the analysis's job, done before you were invoked.

## Filing the candidates

Take the candidates from the conversation: the analysis has just run in this session, and its
list is what you shape.

When you are handed the path to the analysis's HTML report instead — a cleared context has
lost the list, and the report on disk is what is left of it — read the candidates from that
file and file the same issues you would have filed from the conversation.

File one issue per module, never one issue per smell. A single smell is one step of a plan,
and a veri run's fixed overhead is too large to spend on one step; the smells a candidate
names in one module become the steps of that module's issue.

Write each issue's acceptance criteria as structural predicates — statements about the code's
shape that are either true or false of the tree, such as "no module outside `billing/`
imports `billing/internal`" — each carrying a runnable check where one exists: the command
whose output settles the predicate, such as a `grep` that must find nothing.

Under a `## Blocked by` heading, list only real blockers: an issue that must land before this
one can start. veri reads every `#N` in that section as a blocker and holds the issue back
until it closes, so a related issue mentioned there for context is a queue stalled for
nothing; write `None (can start immediately).` when there is none.

End every issue's body with a final `Test command:` line naming the command that runs the
repository's tests — the line veri reads to know how to run them, so nothing may follow it.

A candidate with no checkable predicate, in the sense above, is not filed: an issue whose
criteria no verifier can hold the code against is one veri cannot finish. File nothing for
it, and say which candidate you skipped, by name, and the reason it was skipped, so a dropped
candidate never reads as a complete filing.

Before filing a candidate, look for an issue you already filed for it: list the repository's
issues with `gh issue list --state all --search "<module> in:title"` and read their titles.
When an existing issue already covers that module, do not file it again — a re-run over the
same candidates, after a cleared context or over the same report, files no duplicate.

File each issue with `gh issue create`.
