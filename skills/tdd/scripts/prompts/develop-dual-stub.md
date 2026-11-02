{{SHARED}}

## Phase: develop-dual-stub

This is the **dual-stub** phase of an interface change that supersedes frozen cases. Only
tests change. Production stays as it is, so the cases run against unmoved production code.

{{INCLUDE:_develop-interface-change.md}}

1. Edit only tests. Every case you edit that pins the old transport also stubs the new one,
   and still passes against the unmoved production code; remove or weaken no assertion.
2. {{INCLUDE:_develop-run-affected.md}}
3. Commit the change, as `refactor: <what changed> (#<issue>)`. Never modify a production file: a dual-stub commit that touches one is rejected.

{{INCLUDE:_develop-transform-suite-report.md}}
