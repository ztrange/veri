# Plan for #162 — Verifier prompts never got the foreground rule, so a verifier can end on a background suite with no VERDICT

- [x] The built prompt for each of `red`, `green`, `refactor` and `pin` tells the verifier to run test commands in the foreground and not to end its turn before a suite run has exited
- [x] The built developer prompt for each phase forbids ending the turn while a suite run is still going, not only writing the report during it ⟂ refactor pending
