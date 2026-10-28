# Plan for #2564 — A draft-payload pull_request run cancels the run executing gates and then skips it

- [x] A `pull_request` event whose payload says the PR is a draft cancels no in-progress run for that PR: `cancel-in-progress` in `.github/workflows/ci.yml` evaluates false for a draft-payload `pull_request` event, pinned by a small unit case in a new `skills/tdd/scripts/tests/py/unit/test_workflow_concurrency.py` that evaluates the workflow's concurrency expression against a draft payload without calling GitHub ⟦criterion 1⟧
- [ ] A non-draft `pull_request` event still cancels the previous in-progress run for that PR: `cancel-in-progress` evaluates true for a `pull_request` event whose payload says not draft, pinned the same way in `test_workflow_concurrency.py` ⟦criterion 2⟧
- [ ] The `gates` job's `if:` condition still evaluates false (job skipped) for a `pull_request` event whose payload says draft, pinned the same way in `test_workflow_concurrency.py` ⟦criterion 3⟧
- [ ] The `gates` job's `if:` condition still evaluates true (job runs) for a `pull_request` event whose payload says not draft, and for a `push` event, pinned the same way in `test_workflow_concurrency.py` ⟦criterion 3⟧
- [ ] The go-red control: with the draft condition removed from `cancel-in-progress`, the first criterion's check goes red — watched red by hand and restored ⟦human-owed⟧ ⟦criterion 4⟧
