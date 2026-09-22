# Plan for #415 — The verifier leaf is launched outside supervise.sh, so a dead verifier stalls the run forever

- [x] A suite fails when a verifier launch line in SKILL.md reaches verify.sh without supervise.sh on the same line, and every verifier launch in SKILL.md carries it the way the developer launches do ⟦criterion 1⟧
- [x] A wait on a verifier whose supervisor died ends with exit 2 instead of polling to its deadline, and SKILL.md reports that verifier the way it reports a killed developer leaf ⟦criterion 2⟧
- [x] A supervised verifier launch passes verify.sh only the phase, the spec file, the test path and the test id — or the base sha for refactor — so nothing the supervisor adds can carry the developer's rationale ⟦criterion 3⟧
- [x] A supervised verification still writes only the verdict text to .tdd/verify-<phase>.reason, and a malformed verdict still reaches the conductor as 2 while a REJECT reaches it as 1 ⟦criterion 4⟧
- [x] The launch guard is known to go red: a planted verifier launch line missing supervise.sh makes the suite fail and name that line, so the contradiction cannot return as prose ⟦criterion 5⟧
- [x] A verifier killed before it answered leaves no verdict event in the run's event log while one that answered does, so a stalled wait is never read as a verdict ⟦criterion 6⟧
- [ ] A verification whose leaf is working while the launch wrapper around it stays silent is not killed for that silence, so supervising the wrapper adds no second heartbeat window
