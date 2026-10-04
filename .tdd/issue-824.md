# Plan for #824 — veri/github.py answers what its two remaining Python callers pin: the JSON-decode line on a non-JSON REST answer, and gh_issue_create

- [ ] gh_issue_view, with the GraphQL call failing and gh api exiting non-zero with empty stdout, raises NoAnswer and leaves on stderr gh api's stderr followed by `json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)` and a newline, the GraphQL stderr not passed on (the both-routes-fail case's expectation changes to this) ⟦criterion 1⟧
- [ ] gh_issue_view, with the GraphQL call failing and gh api exiting 0 with a non-JSON stdout, raises NoAnswer with the JSONDecodeError line on stderr ⟦criterion 2⟧
- [ ] gh_issue_view, with the GraphQL call failing and gh api exiting non-zero with a JSON stdout (a REST error body such as {"message":"Not Found"}), raises NoAnswer with no decode line on stderr ⟦criterion 3⟧
- [ ] gh_issue_create("T", "B") runs exactly ["gh", "api", "repos/{owner}/{repo}/issues", "-f", "title=T", "-f", "body=B", "-q", ".html_url"] as its only command and answers that command's stdout ⟦criterion 4⟧
- [ ] gh_issue_create, when gh api exits non-zero, raises NoAnswer with gh's stderr passed through to stderr ⟦criterion 4⟧
- [ ] every pre-existing case of tests/py/test_github.py other than the both-routes-fail case is unmodified by the branch, and lib/github.sh and tests/unit/github.test.sh are unmodified ⟦diff-checked⟧ ⟦criterion 5⟧
