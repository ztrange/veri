{{SHARED}}

## Phase: develop-contract-b

This is the **contract-b** phase of an interface change. Neither product code nor any
test calls the old interface any more; the old interface's proxy is deleted. Behaviour
does not change: every test that was green stays green, and test files stay frozen.

{{INCLUDE:_develop-interface-change.md}}

1. Delete the old interface's proxy from production.
2. {{INCLUDE:_develop-run-affected.md}}
3. Commit the change, as `refactor: <what changed> (#<issue>)`. Never modify
   a test file: a contract-b commit that touches one is rejected.

{{INCLUDE:_develop-transform-suite-report.md}}
