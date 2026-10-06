# Plan for #992 — the refactor leaf reports an out-of-scope candidate in its own class, so the structural pass spends no predicate leaf on it

- [x] `refactor-owed.sh append` over a report with one `CANDIDATES: out-of-scope | …` line and no structural line records it in the owed file, and `refactor-owed.sh list` over that file then exits 3 and prints nothing ⟦criterion 1⟧
- [x] `refactor-owed.sh render` over an owed file holding an out-of-scope candidate prints the transform under its own out-of-scope heading, not under a step heading of `## Refactor owed` and not under `### Test-only` ⟦criterion 2⟧
- [x] `refactor-overflow.sh <n> <owed-file> 0` over an owed file holding only an out-of-scope candidate files one `Refactor owed by #<n>` issue whose body lists that transform (gh faked) ⟦criterion 3⟧
- [x] `refactor-triage.sh` over a report whose only candidate is `CANDIDATES: out-of-scope | …` exits 3 with nothing on stdout, as it does for a cosmetic-only report ⟦criterion 4⟧
- [x] `prompts/develop-refactor.md` defines the out-of-scope class beside structural, cosmetic and test-only, tells the leaf to use it instead of `structural` for a transform outside the issue's bounds or ruled out by its spec, and its `CANDIDATES:` grammar line names it, pinned as text ⟦criterion 5⟧
- [ ] SKILL.md's structural pass hands an owed file's out-of-scope candidates to `refactor-overflow.sh` even when the pass skipped nothing or ran no candidate (`list` exit 3), so they are still filed as `Refactor owed by #<n>`, pinned as text
