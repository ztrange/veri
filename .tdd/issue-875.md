# Plan for #875 — verify-diff rejects every ⟦diff-checked⟧ step that follows a Red/Green step

- [x] build-verify-prompt.sh diff takes the step's own base sha after the branch point (`diff <spec> <branch-base-sha> <step-base-sha>`) and its prompt judges the criterion against `git diff <branch-base-sha>..HEAD` while the "adds no test" REJECT applies only to a test added in `git diff <step-base-sha>..HEAD`, so a test an earlier Red/Green step added is not a ground to REJECT
- [ ] build-verify-prompt.sh diff refuses with exit 2 and no stdout when the step base sha is missing or is not 7-40 lowercase hex characters
- [ ] SKILL.md's ⟦diff-checked⟧ section records the step's base sha (`git rev-parse HEAD` before the develop-diff leaf runs) and passes it to the blind diff verifier after the branch point, `run-verdict.sh --step "<STEP>" diff <spec-file> <branch-base-sha> <step-base-sha>`
