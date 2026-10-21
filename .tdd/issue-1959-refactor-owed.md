### For a unit not at the repository root (e.g. `skills/veri-dev/SKILL.md`, the path given relative to the working directory the step runs from), a `### SKILL.md` heading holding only its bare basename contributes no rows to the unit's list ⟦criterion 1⟧
- rename `_issue_rows`'s parameter `name` to `unit`, since `apply` passes the repo-relative unit path and the function now matches headings against it, not a basename
- inline `_grade` into its two call sites, or have `_guard` share it with `_captured`
