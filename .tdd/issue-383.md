# Plan for #383 — dashboard: the Tests pane matches leaf Bash calls against the spec's Test command, which no leaf has typed since #342

- [x] timed-test-run.sh records the test command's exit status on its `test-run` event, so a reader can say whether that run passed ⟦criterion 2⟧
- [x] /api/tests lists one entry per `test-run` mark in the selected run's event log, rather than per leaf Bash call matching the spec's command ⟦criterion 1⟧
- [x] each /api/tests entry names the suites that test run covered and whether it passed ⟦criterion 2⟧
- [x] a run whose event log holds no `test-run` mark answers an empty tests list, and a run's entries never include another run's test runs ⟦criterion 3⟧
