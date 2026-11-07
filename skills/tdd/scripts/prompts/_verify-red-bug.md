### This issue is a bug, so the red bar itself is the claim

The spec above carries a `## Bug` section naming the headings *What happened*, *Expected*,
*Steps to reproduce* and *Environment* of the report as it was filed, which stands in the
issue body, so this step's case is a **reproduction**: the code's current, wrong behaviour
is what the case has to catch. You are the only party who checks that by running it, because the developer's
account of the run does not reach you. So check 2 is stricter here than it reads: PASS
requires the failure you observe to match the behaviour *What happened* describes.

A test that fails for any other reason is a REJECT naming that reason — including the
error-on-the-name red check 2 otherwise allows, which says nothing about the defect that
was reported. Read *Steps to reproduce* for the conditions the case owes and *Expected* for
the behaviour it asserts; *Environment* tells an incidental detail of the reporter's setup
from a condition the behaviour depends on.
