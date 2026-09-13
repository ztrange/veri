# Plan for #144 — A leaf runs the suite it touched; the full suite runs once in develop-green and in the blind verifiers

- [x] The built develop-red prompt tells the leaf to run the suite holding its new case rather than the full suite, and to fall back to the test command, saying so in its report, when the repository cannot run one suite
- [x] The built develop-green prompt says to iterate on the target case's suite and to run the full suite exactly once, immediately before the SUITE: report line
- [x] The built develop-refactor prompt says to run the suites covering the touched files after its transform rather than the full suite, names verify-refactor as where the full suite runs, and states the trade-off that a break in an untouched suite surfaces there
- [x] The built verify-green and verify-refactor prompts still require the project's full test suite, pinned by a test that has been watched to fail with the sentence removed
- [ ] Every built developer prompt says to run test commands in the foreground and to report only after they exit
- [ ] build-verify-prompt.sh accepts the same arguments as before, so no new parameter reaches a verifier
- [ ] SKILL.md where it describes each phase's leaf, and CLAUDE.md where it describes suite runs, say which leaves run the full suite
