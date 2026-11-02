{{SHARED}}

## Phase: verify-dual-stub

This is the **dual-stub** phase: it edits tests only, so the cases that pin the old transport
stub the new one too. Production stays frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **Production stays frozen.** A range that touches a production file is a REJECT.
3. **Both transports are stubbed.** REJECT a diff in which an edited case does not stub both
   transports.
4. **The edited cases pass against unmoved production code.** Run them at the range's tip
   against the production code as it stands; a case that fails against unmoved production code
   is a REJECT.
5. **No assertion is lost.** REJECT a diff in which an assertion is removed or weakened.{{LAST_PHASE_CHECK}}

PASS if the suites are green, no production file changed, every edited case stubs both
transports and passes against unmoved production code, and no assertion was removed or weakened.
REJECT, naming the specific problem, otherwise.
