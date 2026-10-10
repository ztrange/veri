{{SHARED}}

## Phase: verify-migrate

A developer agent has finished the **migrate** phase of an interface change (the code
around `{{TEST_PATH}}`). In the migrate phase the product callers of the old interface move
to the new interface, and the old interface stays in place. Behaviour does not change, and
test files stay frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The callers moved.** Every product caller of the old interface now calls the new
   interface.
3. **The old interface stays.** Removing it is the contract phase's work.
4. {{INCLUDE:_verify-tests-frozen.md}}

PASS if the suites are green, every product caller moved to the new interface and no test
file changed. REJECT, naming the specific problem, otherwise.
