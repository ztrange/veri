# Plan for #240 — skill-metrics.test.sh's commit-before-PR ordering case passes in either order since #236 merged the Draft PR commands into one sub-step

- [x] The ordering case reads the Draft PR step's fenced command block line by line and fails when the `metrics:` commit line precedes the `gh pr create` line
- [x] The ordering case fails when the `gh pr edit` line precedes the `metrics:` commit or `push-branch.sh`
- [x] The ordering case passes on SKILL.md's current order (gh pr create → event.sh done → metrics.sh → metrics: commit → push-branch.sh → gh pr edit)
- [x] The 📊-in-PR-body probe asks the `gh pr edit` command, not a record that merely also contains `gh pr create`
- [x] The suite's header comment describes the post-#236 Draft PR order ⟂ refactor pending
