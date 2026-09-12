# Plan for #120 — A 'Test command:' line in the issue overrides the detected test command for that run

- [ ] `detect-test-command.sh --issue <body-file> [repo-root]` answers the first `Test command: <cmd>` line of that file, verbatim, ahead of `.veri/test-command` and every inference
- [ ] with no such line in the file, or with no `--issue` at all, the answer is exactly today's: the override file, then the inferences, exit 3 when none matches
- [ ] SKILL.md's preflight reads the issue body for the line before the baseline run, that result is the `<test-cmd>` every leaf gets, and the plan comment states the command in use — pinned as text, the way `skill-identity.test.sh` pins SKILL.md
