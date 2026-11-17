{{SHARED}}

## Phase: develop-break

This is a **legacy** run: the step below names one **region** of code no test covers (a file and a
symbol or line range) and one **seam** that is meant to drive it. A seam leaf found that the named
seam does **not** reach the region without an edit. Make the region reachable from outside it with
**exactly one** dependency-breaking edit from the catalogue `LEGACY.md` names, and nothing else:

- **`sprout`**: move the region's code, unchanged, into a new function or class that the old code
  now calls and a test can call directly.
- **`extract and override`**: extract one dependency call the region makes into a method a test
  may override.

No other edit is allowed: no other refactoring, no behaviour change, no new test, and no edit to
any test file. The existing suite is the only net under this edit, so every caller of the region
must see exactly the behaviour it saw before.

### The step whose region to make reachable

{{STEP}}

{{INCLUDE:_develop-spec-context-only.md}}

1. Read the step; find the region and the seam it names, and why that seam does not reach it.
2. Choose the one catalogued edit that gives the region a seam a test can drive from outside it.
3. Apply it. Move code unchanged; keep every signature the region's existing callers use.
4. {{INCLUDE:_develop-run-affected.md}}
5. Commit the edit as one commit, as `refactor: <the edit and the region> (#<issue>)`. Never
   modify a test file: a break commit that touches one is rejected.

REPORT-FORMAT break | keys BREAK: SEAM: SUITE: | suite required

### Report (last lines of your output)

BREAK: sprout | extract and override
SEAM: <the function, class or method the edit made, through which a test now drives the region>
SUITE: GREEN | RED — <the final summary line of that run>
