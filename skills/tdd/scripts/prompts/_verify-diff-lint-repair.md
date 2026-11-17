This step repairs the findings of the repo's declared lint command. Run the repo's declared lint
command, `{{LINT_CMD}}`, at the worktree root, in the foreground, and read its exit status. REJECT,
naming its first finding, while it exits non-zero: the step is done only when that command passes.
