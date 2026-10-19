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

## Step 2 — VERI_GH_DRIVER, VERI_GH_JSON and #879 head-sha (9/9, exit 0)

| bash case | kept pytest case | mutation | result |
|---|---|---|---|
| with VERI_GH_DRIVER unset, gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready run only gh api, never gh issue or gh pr, and return 2 when gh api fails | `test_with_the_driver_unset_every_graphql_operation_runs_only_gh_api_and_returns_2_when_it_fails` | an unset driver opens routes as `auto` instead of `rest` | proven |
| with VERI_GH_DRIVER=rest, gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready answer from gh api alone, never gh issue or gh pr, and return 2 with gh api's stderr when it fails | `test_with_the_driver_rest_every_graphql_operation_answers_from_gh_api_alone_and_passes_its_stderr_on` | `rest` opens the GraphQL route too | proven |
| with VERI_GH_DRIVER=graphql, gh_issue_view, gh_list, gh_json with gh args and gh_pr_ready return 2 with no gh api call when GraphQL fails, and answer GraphQL's stdout when it succeeds | `test_with_the_driver_graphql_every_graphql_operation_returns_2_without_gh_api_when_graphql_fails` | `graphql` falls back to `gh api` | proven |
| gh_issue_edit, gh_rest_list and gh_json with no gh args run their gh api call and no gh issue or gh pr call under VERI_GH_DRIVER unset, auto, rest and graphql | `test_operations_with_no_graphql_route_run_gh_api_and_no_gh_issue_or_pr_under_every_driver` | gh_issue_edit's PATCH runs only on the REST route, skipped under `graphql` | proven |
| with VERI_GH_DRIVER empty, REST or gql, every gh_* function starts no gh process, returns 2 and prints one stderr line naming VERI_GH_DRIVER and the value | `test_with_the_driver_empty_or_unknown_every_gh_function_starts_no_gh_and_names_the_variable_and_value` | an empty driver is accepted as `rest` | proven |
| with VERI_GH_JSON set, gh_json with and without gh args prints the fixture file's contents and starts no gh or python3 process under VERI_GH_DRIVER unset, auto, rest and graphql | `test_with_veri_gh_json_set_gh_json_prints_the_fixture_and_starts_no_gh_or_python3_under_every_driver` | gh_json reads the fixture name without the `$VERI_GH_JSON/` directory | proven |
| #879 gh_pr_ready 42 <head-sha> marks PR 42 ready only after pulls/42 reports <head-sha> as its head, reading it again after VERI_POLL seconds while it reports another | `test_gh_pr_ready_with_a_head_sha_marks_ready_only_after_pulls_42_reports_it_polling_every_veri_poll` | the poll sleeps a fixed 10 s, ignoring VERI_POLL | proven |
| #879 gh_pr_ready 42 <head-sha> returns 2 without marking PR 42 ready when pulls/42 still reports another sha after its bounded number of reads, naming both shas on stderr | `test_gh_pr_ready_with_a_head_sha_returns_2_unready_naming_both_shas_when_pulls_42_never_reports_it` | running out of reads breaks to marking ready instead of returning 2 | proven |
| #879 gh_pr_ready 42 with no head-sha marks PR 42 ready at once, reading no pulls/42 and never sleeping | `test_gh_pr_ready_with_no_head_sha_marks_ready_at_once_reading_no_pulls_42_and_never_sleeping` | with no head-sha the poll loop still reads pulls/42 and sleeps | proven |
