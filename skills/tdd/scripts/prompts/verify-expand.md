{{SHARED}}

## Phase: verify-expand

A developer agent has finished the **expand** phase of an interface change (the code
around `{{TEST_PATH}}`). The expand phase adds the new interface to production, and the
old interface becomes a proxy that delegates to it. Behaviour does not change, and test
files stay frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The new interface exists.** Production gains the new interface the step names.
3. **The old interface is a proxy.** The old interface delegates to the new one; no caller
   has moved yet.
4. **Test files stay frozen.** A range that touches a test file is a REJECT.

PASS if the suites are green, the new interface exists, the old one is a proxy over it and
no test file changed. REJECT, naming the specific problem, otherwise.
