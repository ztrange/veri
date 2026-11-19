# Plan for #4376 — The diff verifier and pin recheck take --branch-base <sha> from the conductor's record, not a remote-tracking ref

- [x] `pin-recheck.sh` with `--branch-base` missing, or not matching `^[0-9a-f]{7,40}$`, exits 2 naming the flag ⟦criterion 2⟧
- [x] `pin-recheck.sh`'s base worktree and its named-test-file check use the `--branch-base` sha, not `origin/main`, when `origin/main` is rewritten ⟦criterion 1⟧
- [x] `step-close.sh` hands `pin-recheck.sh` the run's recorded branch base, and stops with exit 2 when the record is missing or not hex ⟦criterion 3⟧
- [x] the `diff` verifier (`verify.sh`, `run-verdict.sh`) takes its branch base from `--branch-base` as `diff <spec-file> <step-base-sha>`, not a positional sha, when `origin/main` is rewritten ⟦criterion 1⟧
- [ ] the `diff` verifier with `--branch-base` missing or malformed, or a third positional, exits 2 naming the flag ⟦criterion 2⟧
- [ ] `DIFF-CHECKED.md`, `REVISE.md`, `SKILL.md` and `SCRIPTS.md` pass the recorded base at every diff-verifier and pin-recheck call site, with rows CY411 and SC601, graded ⟦criterion 3⟧
