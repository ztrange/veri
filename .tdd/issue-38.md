# Plan for #38 — build-develop-prompt.sh: developer-leaf prompts become versioned templates

- [x] build-develop-prompt.sh red builds a prompt carrying the spec, the step text and the test command verbatim, and the AGAINST_UNMODIFIED report line
- [x] build-develop-prompt.sh green builds a prompt carrying the test path and target test and the do-not-modify-the-test instruction
- [x] build-develop-prompt.sh refactor builds a prompt carrying the touched-files list and the no-untested-generality rule, with the RESULT/FLAGS footer
- [ ] build-develop-prompt.sh revise builds a prompt carrying the rejection reason verbatim and the IMPOSSIBLE outcome
- [ ] an unknown phase or a missing template, spec or reason file exits 2 with a diagnostic and prints no prompt
