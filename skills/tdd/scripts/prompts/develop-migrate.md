{{SHARED}}

## Phase: develop-migrate

This is the **migrate** phase of an interface change. The new interface exists and the old
one is a proxy over it; the callers move to the new interface. Behaviour does not change:
every test that was green stays green, and test files stay frozen.

{{INCLUDE:_develop-interface-change.md}}

1. Move every product caller of the old interface to the new interface. Leave the old
   interface in place: removing it is the contract phase.
2. {{INCLUDE:_develop-run-affected.md}}
3. Commit the change, as `refactor: <what changed> (#<issue>)`. Never modify
   a test file: a migrate commit that touches one is rejected.

{{INCLUDE:_develop-transform-suite-report.md}}
