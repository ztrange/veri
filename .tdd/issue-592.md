# Plan for #592 — gh api --paginate follows repositories/{id} next links, which the cloud session's proxy refuses, so every list longer than a page exits 2

- [x] With a gh stub that serves a list over three pages on repos/{owner}/{repo}/…?page=N (each page carrying a Link rel="next" pointing at repositories/{id}/…) and refuses any repositories/ path with the proxy's HTTP 403, gh_rest_list prints every item from all three pages and exits 0 ⟦criterion 1⟧
- [x] With that same three-page stub, and the gh subcommand route failing, gh_list falls back to REST and prints every item from all three pages and exits 0 ⟦criterion 1⟧ ⟂ refactor pending
- [ ] With that same stub, invisible-work.sh gives the output it gives against a single-page fixture holding the same issues and PRs ⟦criterion 2⟧
- [ ] With that same stub, workqueue.sh gives the output it gives against a single-page fixture holding the same issues ⟦criterion 2⟧
- [ ] With that same stub, solvable-issues.sh gives the output it gives against a single-page fixture holding the same issues and PRs ⟦criterion 2⟧
- [ ] With that same stub, parallel-conductors.sh gives the output it gives against a single-page fixture holding the same PRs ⟦criterion 2⟧
- [ ] wait-ci.sh reads check-runs spread over more than one page through that stub and reaches the same verdict as with the same check-runs on one page ⟦criterion 3⟧
- [ ] When a page request after the first fails for a reason other than the proxy refusal (network error, HTTP 5xx), gh_rest_list and gh_list exit 2 ⟦criterion 4⟧
- [ ] When a check-runs page request after the first fails for a reason other than the proxy refusal, wait-ci.sh treats it as no answer from GitHub, exactly as it treats a failed single-page read ⟦criterion 4⟧
- [ ] CI (Linux) stays green ⟦full-suite⟧ ⟦criterion 5⟧
