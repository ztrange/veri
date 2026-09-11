# Plan for #63 — Make build-develop-prompt.sh refuse an unknown phase and a bad revise target with exit 2

- [x] `build-develop-prompt.sh bogus` with no further arguments exits 2, prints a diagnostic naming the unknown phase to stderr, and prints nothing to stdout
- [x] `build-develop-prompt.sh revise bogus <spec-file> <step-text> <test-cmd> <reason-file>` exits 2 with a diagnostic on stderr and prints nothing to stdout
- [x] `build-develop-prompt.sh red <spec-file>` (a valid phase, missing positionals) exits 2, not 1, with a diagnostic on stderr and nothing on stdout
- [ ] `build-develop-prompt.sh` with no arguments at all exits 2 with a usage diagnostic on stderr and nothing on stdout
