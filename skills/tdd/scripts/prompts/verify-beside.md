{{SHARED}}

## Phase: verify-beside

This is the **beside** phase: it adds the new interface to production beside the old one, and
the old interface keeps its behaviour. Test files stay frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The new interface exists.** Production gains the new interface the step names.
3. **The old interface is untouched.** REJECT a diff that changes the old interface's behaviour,
   or that turns it into a proxy over the new interface.
4. {{INCLUDE:_verify-tests-frozen.md}}{{LAST_PHASE_CHECK}}

PASS if the suites are green, the new interface exists, the old one behaves as before with no
proxy and no test file changed. REJECT, naming the specific problem, otherwise.
