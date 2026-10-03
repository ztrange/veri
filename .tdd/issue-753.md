# Plan for #753 — a verifier launched with no open step gets --step "" and verify.sh answers it with exit 1, not 2

- [x] verify.sh given `--step ""`, or a trailing `--step` with no value, exits 2, names `--step` on stderr and launches no verifier leaf ⟦criterion 1⟧
- [x] a `verdict-<phase>` supervision of run-verdict.sh whose verify.sh refused its arguments with exit 2 records 2 in `.tdd/verdict-<phase>.exit` and exits 2, never 1, so the conductor's wait never reads a bad argument as a REJECT ⟦criterion 1⟧
- [x] SKILL.md's verify-rebase launch line passes a `--step` that falls back to the last done step's text (`ledger-steps.sh last-done`) when `ledger-steps.sh current` prints nothing ⟦criterion 2⟧
- [x] SKILL.md's structural pass spells the transform verifier's launch line, and its `--step` falls back to the last done step's text when no step is open ⟦criterion 2⟧
- [x] SKILL.md's general verifier launch shape and the revise loop's re-verify line fall back to the last done step's text when no step is open, so an end-of-run verifier launches first time ⟦criterion 2⟧
- [x] `make test` is green ⟦full-suite⟧ ⟦criterion 3⟧
