{{SHARED}}

## Phase: develop-cover-new

This is the **cover-new** phase of an interface change. The expand phase added the new
interface; before any caller moves onto it, it gets tests of its own. Cases are added,
and production stays frozen.

{{INCLUDE:_develop-interface-change.md}}

1. Add cases that call the new interface directly, each pinning a behaviour the step
   names. Leave every existing case and every caller as they are.
2. {{INCLUDE:_develop-run-affected.md}}
3. Commit the change, as `test: <what changed> (#<issue>)`. Never modify a
   production file: a cover-new commit that touches one is rejected.

{{INCLUDE:_develop-transform-suite-report.md}}
