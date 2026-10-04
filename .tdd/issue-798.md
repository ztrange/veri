# Plan for #798 — veri/github.py is the one place Python reads GitHub, with lib/github.sh's GraphQL→REST fallback behaviour unchanged

- [ ] veri.github.gh_rest_list requests `gh api <rest-path>?page=1`, `page=2`, … and answers every page's body back to back with no separator, stopping at the first page that is a bare `[]`, which is not part of the answer ⟦criterion 1⟧
- [ ] veri.github.gh_rest_list requests `&page=N` when the rest path already holds a `?`, and stops at the first page matching a caller-given empty pattern such as wait-ci.sh:80's `"check_runs": *\[ *\]` ⟦criterion 1⟧
- [ ] veri.github.gh_rest_list is a no-answer when any page's `gh api` call fails, a failure on page 2 included, with gh's stderr passed through ⟦criterion 1⟧
- [ ] veri.github.gh_list answers the stdout of `gh <gh args…>` when that call succeeds, and makes no `gh api` call ⟦criterion 1⟧
- [ ] veri.github.gh_list, when the `gh <gh args…>` call exits non-zero, answers gh_rest_list's pages for the rest path without passing that call's stderr on, and is a no-answer when the REST route fails ⟦criterion 1⟧
- [ ] veri.github.gh_issue_view answers `gh issue view <n> --json body -q .body`'s output for body and `gh issue view <n> --json labels -q '.labels[].name'`'s for labels when that call succeeds, and makes no `gh api` call ⟦criterion 1⟧
- [ ] veri.github.gh_issue_view, when the `gh issue view` call exits non-zero, answers the issue's body from `gh api repos/{owner}/{repo}/issues/<n>` without passing the GraphQL call's stderr on, and is a no-answer when that `gh api` call fails ⟦criterion 1⟧
- [ ] veri.github.gh_issue_view's REST route answers "" for a null body and the label names one per line for labels, and a non-JSON REST answer is a no-answer ⟦criterion 3⟧
- [ ] veri.github.gh_issue_edit replaces issue <n>'s body by `gh api -X PATCH repos/{owner}/{repo}/issues/<n> -F body=@<body-file>`, discarding its stdout, and is a no-answer with gh's stderr passed through when that call fails ⟦criterion 1⟧
- [ ] veri.github.gh_json with VERI_GH_JSON set answers the fixture file's contents and makes no subprocess call ⟦criterion 2⟧
- [ ] veri.github.gh_json with VERI_GH_JSON unset takes the REST-only gh_rest_list path when given no gh args, and the gh_list path when given gh args ⟦criterion 2⟧
- [ ] veri/github.py is importable as `from veri import github` and as `import veri.github`, and importing it starts no process and holds no state ⟦criterion 4⟧
- [ ] the PR body lists the Python modules already copying the fallback — veri/capture_spec.py:14-32 on main, and veri/coverage_blocker.py in #794 — as follow-ups ⟦human-owed⟧ ⟦criterion 5⟧
- [ ] lib/github.sh, its seven bash users, tests/unit/github.test.sh and tests/no-graphql-gh-calls.test.sh are unmodified by the branch ⟦diff-checked⟧ ⟦criterion 6⟧
- [ ] the full suite, those files' suites included, passes ⟦full-suite⟧ ⟦criterion 6⟧
