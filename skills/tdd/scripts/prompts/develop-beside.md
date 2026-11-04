{{SHARED}}

## Phase: develop-beside

This is the **beside** phase of an interface change that supersedes frozen cases. Production
gains the new interface beside the old one. The old interface's behaviour stays unchanged: it
is not turned into a proxy over the new one, so there is no proxy. Test files stay frozen.

{{INCLUDE:_develop-interface-change.md}}

1. Add the new interface to production, beside the old one, with no proxy. Leave the old
   interface's behaviour unchanged. Move no caller: that is the migrate phase.
2. {{INCLUDE:_develop-run-affected.md}}
3. Commit the change, as `refactor: <what changed> (#<issue>)`. Never modify a test file: a beside commit that touches one is rejected.

{{INCLUDE:_develop-transform-suite-report.md}}
