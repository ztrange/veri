{{SHARED}}

## Phase: verify-expand

This is the **expand** phase: it adds the new interface to production, and the old interface
becomes a proxy that delegates to it. Test files stay frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The new interface exists.** Production gains the new interface the step names.
3. **The old interface is a proxy.** The old interface delegates to the new one; no caller
   has moved yet.
4. {{INCLUDE:_verify-tests-frozen.md}}

PASS if the suites are green, the new interface exists, the old one is a proxy over it and
no test file changed. REJECT, naming the specific problem, otherwise.
