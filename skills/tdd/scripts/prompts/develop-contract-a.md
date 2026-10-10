{{SHARED}}

## Phase: develop-contract-a

This is the **contract (a)** phase of an interface change. No product caller of the old
interface remains; the tests that still exercise it move off it. Tests are rewritten or
deleted, and production stays frozen.

{{INCLUDE:_develop-interface-change.md}}

1. Rewrite every test of the old interface against the new one, or delete it where a
   test of the new interface already covers the same behaviour. Leave the old interface
   in place: deleting its proxy is contract (b).
2. {{INCLUDE:_develop-run-affected.md}}
3. Commit the change, as `refactor: <what changed> (#<issue>)`. Never modify a
   production file: a contract (a) commit that touches one is rejected.

{{INCLUDE:_develop-transform-report.md}}
SUITE: GREEN | RED — <the final summary line of that run>
