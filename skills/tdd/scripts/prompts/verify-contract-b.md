{{SHARED}}

## Phase: verify-contract-b

This is **contract (b)**: the proxy over the old interface is deleted. Test files stay
frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The proxy is deleted.** The old interface no longer exists in production.
3. {{INCLUDE:_verify-tests-frozen.md}}

PASS if the suites are green, the proxy is deleted and no test file changed. REJECT, naming
the specific problem, otherwise.
