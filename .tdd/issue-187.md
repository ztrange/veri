# Plan for #187 — A /tdd run started inside a Claude Code session fails at its first leaf

- [x] A preflight check establishes that a leaf can actually be launched, refusing with a diagnostic that names the cause and the supported invocation — asked of the capability, not of one variable's name (criterion 1, amended 2026-09-15: the `CLAUDECODE` guard no longer fires, so the literal wording would refuse a working configuration)
- [x] That refusal creates no worktree, writes no spec, runs no test command and posts no issue comment
- [x] When a leaf can be launched, the check passes and the run proceeds exactly as it does today
- [x] `SKILL.md` states the supported way to launch the conductor from an operator's own session, and records that veri never unsets the guard itself ⟂ refactor pending
- [ ] `SKILL.md`'s preflight runs `leaf-launchable.sh` before the baseline, so the check the earlier steps built is the one a real run performs
