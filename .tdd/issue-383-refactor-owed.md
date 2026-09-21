### /api/tests lists one entry per `test-run` mark in the selected run's event log, rather than per leaf Bash call matching the spec's command
- fold the three near-identical `test-run` fixture lines in the marks case into one printf template over `(tier, suites, seconds, status)`, the way the events case writes its thirty launches — left undone because for three lines the loop plus five variables reads worse than the three literals it replaces
- extract the `if [[ -n "$module_problem" ]] … / "calling $module.<fn> wrote nothing"` scaffold repeated 11 times in `dashboard.test.sh` into one helper — beyond a cycle's tidy-up: 10 of the 11 copies are cases this cycle did not write
### each /api/tests entry names the suites that test run covered and whether it passed
- the five Tests cases each write their own `issue-<n>.md` ledger and `issue-<n>-spec.md` spec inline, differing only in the issue number and the prose — a `fabricate_spec` helper beside `fabricate_marks` would spell the `Test command:` line once (three of the five predate this cycle, so it reaches beyond the cycle's code)
### a run whose event log holds no `test-run` mark answers an empty tests list, and a run's entries never include another run's test runs
- move `tests_json`'s `if command else []` guard into `logged_test_runs`, so the branch decides only which account answers a run and not also what an empty test command means
- `tempty_sel` writes its own `events.jsonl` heredoc while every other case gets one from `fabricate_marks`; a helper writing a log of given marks would spell the line shape once
