{{SHARED}}

## Phase: verify-contract-b

This is **contract-b**: the old interface is deleted (its proxy after expand, the interface
itself after beside). Test files stay frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The old interface is deleted.** The old interface no longer exists in production (its
   proxy after expand, the interface itself after beside).
3. {{INCLUDE:_verify-tests-frozen.md}}{{LAST_PHASE_CHECK}}

PASS if the suites are green, the old interface is deleted and no test file changed. REJECT, naming
the specific problem, otherwise.
