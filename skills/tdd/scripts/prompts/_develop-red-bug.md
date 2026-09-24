### This issue is a bug, so Red is a reproduction

The spec below carries a `## Bug` section — the report as it was filed — which means this
step's case is a **reproduction** rather than a fresh specification. Write the test from
*Expected*: that is the behaviour the code owes and the assertion the case makes. Drive it
with *Steps to reproduce*, using *Environment* only to tell an incidental detail of the
reporter's setup from a condition the behaviour depends on. Before you report, confirm the
case fails with the behaviour *What happened* describes — not with a missing symbol, an
import error or a typo, each of which is a red bar that says nothing about the reported
defect. A failure of any other shape is the test's own bug: it is step 4's divergence,
and the test is what changes.

Name the case so it carries `#<n>`, the issue's number, in whatever the project's
test-naming idiom already is — once it is green it stays as this bug's regression test,
and the number is what says which report it stands for.
