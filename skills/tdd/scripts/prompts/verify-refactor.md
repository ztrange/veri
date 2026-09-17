{{SHARED}}

## Phase: verify-refactor

A developer agent has finished the **refactor** pass for this cycle (the code and test
around `{{TEST_PATH}}`). The refactor is meant to be **behavior-preserving** tidy-up.
The step's green commit, where the refactor started, is `{{BASE_SHA}}`.
Render one verdict on the settled result.

### The issue's behavior spec

{{ISSUE_SPEC}}

### Your checks

1. **Still green.** Run the project's full test suite yourself; it must be **green**. A
   refactor that changed observable behavior or broke any test is a REJECT.
2. **Up to standard.** The settled code should be code you would approve: it follows the
   repository's **conventions**, uses sensible **typing**/structure where the project
   does, names things clearly, and is reasonably **robust** (no obvious unhandled edge
   case the spec implies). It must not have smuggled in untested generality — generality
   is only earned through triangulation, not hand-written here.

PASS if the suite is green and the code is up to standard. REJECT, naming the specific
weakness, if the tidy-up left the code below standard or altered behavior.
