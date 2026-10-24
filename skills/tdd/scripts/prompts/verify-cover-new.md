{{SHARED}}

## Phase: verify-cover-new

This is **cover-new**: it adds cases that call the new interface directly. Production
stays frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The new interface has cases of its own.** The range adds cases that call the new
   interface directly, not through the old interface or its proxy.
3. **Production stays frozen.** A range that touches a production file is a REJECT.{{LAST_PHASE_CHECK}}

PASS if the suites are green, the new interface has cases of its own and no production file
changed. REJECT, naming the specific problem, otherwise.
