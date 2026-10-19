# Mutation-parity pairs proven for #1352

Every row below is `proven` by `mutation-parity.sh` run against the step's pre-deletion tree with `tests/py/test_github_sh.py` added. Each mutation is a one-line edit to `skills/tdd/scripts/lib/github.sh`; every kept case is in `skills/tdd/scripts/tests/py/test_github_sh.py`.

## Step 1 — gh_pr_ready routes and pagination (7/7, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| gh_pr_ready 42 against a gh that answers GraphQL runs gh pr ready 42, returns 0, and never calls pulls/42/ccr/ready_for_review | `test_gh_pr_ready_runs_gh_pr_ready_when_graphql_answers_and_never_calls_the_ccr_route` | after `gh pr ready` succeeds, gh_pr_ready does not return and calls the ccr route anyway | proven |
| gh_pr_ready 42 against a gh that refuses GraphQL with the 403 calls pulls/42/ccr/ready_for_review over gh api and returns 0 | `test_gh_pr_ready_calls_the_ccr_route_over_gh_api_when_graphql_is_refused_with_the_403` | the REST route posts to `pulls/<n>/ready_for_review`, dropping `ccr/` | proven |
| gh_pr_ready 42 returns 2 when gh pr ready fails with a 404, and when pulls/42/ccr/ready_for_review fails with a 502 | `test_gh_pr_ready_returns_2_when_gh_pr_ready_fails_with_a_404_and_when_the_ccr_route_fails_with_a_502` | with no route answering, gh_pr_ready returns 1 instead of 2 | proven |
| gh_rest_list repos/{owner}/{repo}/issues?per_page=2 against a gh serving three pages on repos/…?page=N and refusing repositories/ with the proxy's 403 prints items 1–6 and returns 0 | `test_gh_rest_list_pages_on_the_repos_path_when_the_proxy_refuses_repositories_paths` | gh_rest_list requests every page on `repositories/<id>` | proven |
| gh_rest_list repos/{owner}/{repo}/pulls against a gh serving only repos/{owner}/{repo}/pulls?page=N prints items 1–3 and returns 0 | `test_gh_rest_list_gives_a_path_with_no_query_string_page_n_as_its_query_string` | the page separator is always `&` | proven |
| gh_list repos/{owner}/{repo}/issues?per_page=2 with gh issue list refused and a gh serving three pages on repos/…?page=N and refusing repositories/ with the proxy's 403 prints items 1–6 and returns 0 | `test_gh_list_falls_back_to_rest_paging_on_the_repos_path_when_gh_issue_list_is_refused` | gh_list's REST fallback pages on `repositories/<id>` | proven |
| gh_rest_list and gh_list repos/{owner}/{repo}/issues?per_page=2 return 2 when page 1 answers and page 2 fails with a 502, and with a network error | `test_gh_rest_list_and_gh_list_return_2_when_page_2_fails_with_a_502_and_with_a_network_error` | a failed page breaks the loop and returns 0 instead of 2 | proven |
