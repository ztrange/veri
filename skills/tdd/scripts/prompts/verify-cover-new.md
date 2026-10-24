{{SHARED}}

## Phase: verify-cover-new

This is **cover-new**: it adds cases that call the new interface directly. Production
stays frozen.
{{INCLUDE:_verify-interface-phase-lead.md}}
2. **The new interface has cases of its own.** The range adds cases that call the new
   interface directly, not through the old interface or its proxy.
3. **Production stays frozen.** A range that touches a production file is a REJECT.
4. **The new cases pass at the base.** Check out `{{BASE_SHA}}` in a throwaway worktree
   (`git worktree add --detach <scratch> {{BASE_SHA}}`), put the range's new test cases there,
   and run them: each must pass against the expand commit, else REJECT.
5. **The new cases catch a broken interface.** Mutate the new interface's behaviour yourself
   (copy the file aside with `cp <file> <file>.orig`, change it, run the new cases, put it back
   with `mv <file>.orig <file>`): each new case must go red under a mutation of the behaviour it
   covers, and you must restore the file. A case that stays green is a REJECT.{{LAST_PHASE_CHECK}}

PASS if the suites are green, the new interface has cases of its own, no production file
changed, the cases pass at the base and go red under your mutation. REJECT, naming the specific problem, otherwise.
