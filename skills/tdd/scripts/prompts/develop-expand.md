{{SHARED}}

## Phase: develop-expand

This is the **expand** phase of an interface change. Production gains the new interface,
and the old interface becomes a proxy that delegates to it. Behaviour does not change:
every test that was green stays green, and test files stay frozen.

{{INCLUDE:_develop-interface-change.md}}

1. Add the new interface to production, and turn the old one into a proxy over it.
   Move no caller yet: that is the migrate phase.
2. {{INCLUDE:_develop-run-affected.md}}
3. Commit the change, as `refactor: <what changed> (#<issue>)`. Never modify
   a test file: an expand commit that touches one is rejected.

{{INCLUDE:_develop-transform-suite-report.md}}
