{{SHARED}}

## Phase: verify-contract-b

A developer agent has finished **contract (b)** of an interface change (the code around
`{{TEST_PATH}}`). In contract (b) the proxy over the old interface is deleted. Behaviour
does not change, and test files stay frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The proxy is deleted.** The old interface no longer exists in production.
3. **Test files stay frozen.** A range that touches a test file is a REJECT.

PASS if the suites are green, the proxy is deleted and no test file changed. REJECT, naming
the specific problem, otherwise.
