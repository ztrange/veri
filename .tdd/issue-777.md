# Plan for #777 — refactor-overflow, workqueue, ensure-run-state-ignored and coverage-blocker never lose or duplicate work silently

- [x] refactor-overflow.sh files every candidate in <skipped-file> when refactor-owed.sh list exits 3 (owed file missing, empty, or holding no structural candidate) ⟦criterion 1⟧
- [x] workqueue.sh start, done and park keep a last queue line that has no trailing newline when they rewrite the queue ⟦criterion 2⟧
- [x] workqueue.sh assign onto a queue whose last line has no trailing newline keeps that line intact and puts each new item on a line of its own ⟦criterion 2⟧
- [ ] ensure-run-state-ignored.sh writes both files or neither: when the .gitignore write fails, info/exclude is left byte-identical and it exits 2 ⟦criterion 3⟧
- [ ] coverage-blocker.sh run a second time for the same refactor issue, after a first run that filed the coverage issue and then failed, files no second coverage issue, prints the existing one's URL and blocks the refactor issue on it ⟦criterion 4⟧
- [ ] every case the four scripts' suites already hold passes ⟦full-suite⟧ ⟦criterion 5⟧
- [ ] no assertion of any case the four scripts' suites already held is changed or removed by this branch, except a case asserting one of the four named bugs, whose expectation flips to the fixed behaviour and nothing else ⟦diff-checked⟧ ⟦criterion 5⟧
