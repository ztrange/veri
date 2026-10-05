# Plan for #955 — The baseline runs on the caller's checkout, not the commit the issue branch is cut from

- [x] SKILL.md runs the baseline fast-tier suite inside the issue's worktree, after `issue-worktree.sh` has cut the branch and the conductor has `cd`'d into it, not in the caller's checkout — so with the caller's checkout behind `origin/<default>` the baseline proves the commit the branch is cut from ⟦criterion 1⟧
- [x] SKILL.md says a red baseline in the worktree stops the run before the plan and before any cycle with the same preflight-class report a red baseline gave before, whatever state the caller's checkout is in ⟦criterion 2⟧
- [x] SKILL.md takes the full-tier measurement in that same worktree, on the same commit as the fast-tier baseline, and sizes the hard timeout (`leaf-timeout.sh … --full`) only after that measurement ⟦criterion 3⟧
- [x] SKILL.md says that on resume of an existing branch the baseline runs on that branch's head in its existing worktree, before any cycle of the resumed run starts ⟦criterion 4⟧ ⟂ refactor pending
