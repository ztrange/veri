### For a unit not at the repository root (e.g. `skills/veri-dev/SKILL.md`, the path given relative to the working directory the step runs from), a `### SKILL.md` heading holding only its bare basename contributes no rows to the unit's list ⟦criterion 1⟧
- rename `_issue_rows`'s parameter `name` to `unit`, since `apply` passes the repo-relative unit path and the function now matches headings against it, not a basename
- inline `_grade` into its two call sites, or have `_guard` share it with `_captured`
### A unit with no requirements list yet (no `REQUIREMENTS.md` beside it and no `## Requirements` table in it), run against an issue whose `## Requirements` section states rows for it, raises nothing and those stated rows become its new list in the `REQUIREMENTS.md` beside it ⟦criterion 4⟧
- `_create` and the no-list branch of `apply` both write a new list file, differing only in the heading name (basename versus repo-relative path) and in whether they append to an existing file
### Each author attempt's leaf is launched under the name `author-skill-edit-<k>` for its 1-based attempt number `<k>` (the second attempt is `author-skill-edit-2`) ⟦criterion 5⟧
- replace the module-level `_attempt = [1]` mutable with an `attempt` parameter on `_author`
applied | 50d8a41716cfdfbd18c2459cab3e6e903aae8445 | rename `_issue_rows`'s parameter `name` to `unit`, since `apply` passes the repo-relative unit path and the function now matches headings against it, not a basename
applied | ad7fc1532ca0f0db394d85958638c7ef91fb8cd5 | `_create` and the no-list branch of `apply` both write a new list file, differing only in the heading name (basename versus repo-relative path) and in whether they append to an existing file
