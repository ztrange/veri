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

File one issue per module, never one issue per smell. A single smell is one step of a plan,
and a veri run's fixed overhead is too large to spend on one step; the smells a candidate
names in one module become the steps of that module's issue.

Write each issue's acceptance criteria as structural predicates — statements about the code's
shape that are either true or false of the tree, such as "no module outside `billing/`
imports `billing/internal`" — each carrying a runnable check where one exists: the command
whose output settles the predicate, such as a `grep` that must find nothing.

File each issue with `gh issue create`.
