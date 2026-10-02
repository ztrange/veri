# Plan for #617 — run-suite.sh cannot find the count-line guard when the skill is reached through a symlink or a pinned snapshot

- [x] run-suite.sh over a green suite, invoked through a symlink to the skills/tdd directory placed where no Makefile is three levels up, prints the suite's output and exits 0 ⟦criterion 1⟧
- [x] make test's count-line guard comes from one file under skills/tdd/scripts/lib (the Makefile defines neither the pattern nor the refusal text itself), so changing that file's refusal text changes what make test prints for a countless suite, and make test run from a tree missing that file fails, naming the file, rather than passing every suite ⟦added⟧ ⟦criterion 2⟧
- [x] run-suite.sh over a green suite, run from a git-archive extraction of skills/tdd alone with no Makefile in or above it, prints the suite's output and exits 0 ⟦criterion 2⟧
- [x] run-suite.sh over a green suite, run with the working directory inside a git repository that is not veri and has no Makefile, exits 0 ⟦criterion 3⟧
- [x] run-suite.sh over a red suite (count line with m > 0, non-zero exit) exits with the suite's own code, from the symlinked dir and from the snapshot ⟦criterion 4⟧
- [x] run-suite.sh over a suite that exits 0 without its count line exits 1 and prints `<suite>: never reached its count line`, from the symlinked dir and from the snapshot ⟦criterion 5⟧
- [x] make test over a suite that exits 0 without its count line fails and prints `<suite>: never reached its count line`, byte-identical to what run-suite.sh prints for that suite ⟦criterion 6⟧
- [ ] make test's count-line guard comes from the same file under skills/tdd/scripts/lib that run-suite.sh reads, so changing that file's refusal text changes what make test prints for a countless suite
- [ ] make test over suites that all end in a count line with 0 failed exits 0 ⟦criterion 7⟧
