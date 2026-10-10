# Plan for #1282 — SKILL.md: a conductor never re-runs a failed CI job; a red CI goes to repair or bail

- [x] SKILL.md's Draft PR step states that a conductor never re-runs a failed CI job (no `gh run rerun`, no re-run of a failed check): a red CI check is answered only by the existing repair-step-or-`ci-red`-bail path, and re-running a known flake is the operator's decision, made outside a run ⟦criterion 1⟧
- [x] SKILL.md's `ci-red` bail names the failing CI job: the bail mark and the `### ⛔ Bailed` comment carry the name of each check that failed, read from the PR head's check runs ⟦criterion 1⟧
