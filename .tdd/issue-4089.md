# Plan for #4089 — PRD 016.6a: /vready checks the token's scopes, the selection labels and Actions read

- [x] the `token scopes` row is `ok` when `gh api -i user`'s `X-OAuth-Scopes` header lists `repo` and `origin` is not HTTPS ⟦criterion 1⟧
- [x] over an HTTPS `origin`, a header listing `repo` but not `workflow` fails the row, its fix `gh auth refresh -s workflow` ⟦criterion 1⟧
- [x] a header listing neither fails the row over HTTPS with `gh auth refresh -s repo,workflow` ⟦criterion 1⟧
- [x] with no `X-OAuth-Scopes` header the `token scopes` row reads `not verifiable` ⟦criterion 2⟧
- [x] the `label <VERI_PRIORITY_LABEL's value>` row is `ok` when `gh api repos/{owner}/{repo}/labels/<name>` answers and `fail` on 404, its fix `gh label create <name>` ⟦criterion 3⟧
- [x] a `label bug` row is `ok` when that call answers for `bug` and `fail` on 404, its fix `gh label create bug` ⟦criterion 3⟧
- [x] the `actions read` row is `ok` when `gh api repos/{owner}/{repo}/actions/runs?per_page=1` exits 0 and `fail` otherwise ⟦criterion 4⟧
- [x] with no `.github/workflows/` at the default branch's tip the `actions read` row reads `skipped` ⟦criterion 4⟧
- [x] the `run-state ignore` row is `ok` when `.gitignore` and the common git directory's `info/exclude` each carry the run-state rule or are writable, and `fail` naming the one that is not ⟦criterion 5⟧
- [ ] ready-check.sh prints the new rows, and a `not verifiable` or `skipped` row counts as no fail ⟦criterion 2⟧ ⟦criterion 4⟧
- [ ] across failing answers, every gh call the new rows make is a REST read, none GraphQL, no file is written, every call is gh or git, and each fix is one command or a named settings key ⟦criterion 6⟧ ⟦criterion 7⟧
