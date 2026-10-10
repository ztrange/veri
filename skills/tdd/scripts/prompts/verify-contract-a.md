{{SHARED}}

## Phase: verify-contract-a

A developer agent has finished **contract (a)** of an interface change (the code around
`{{TEST_PATH}}`). Contract (a) moves the tests off the old interface onto the new one.
Behaviour does not change, and production stays frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The tests moved.** No test calls the old interface any more.
3. **Production stays frozen.** A range that touches a production file is a REJECT.

PASS if the suites are green, the tests moved to the new interface and no production file
changed. REJECT, naming the specific problem, otherwise.
