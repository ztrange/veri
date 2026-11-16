# Plan for #3928 — PRD 023.16: park_issue's logic is tested once, in-process, and its shim once

- [x] every case of test_park_issue_process.py that starts only park-issue.sh (and its gh stub) runs in-process through run_cli in unit/test_park_issue.py, with the same argv and cwd and the same asserted exit code, stdout and stderr, each gh stub answering the same calls through fake_processes ⟦criterion 1⟧
- [x] every moved case is small: no process or tree_audit mark, and fast_tier_guard names none ⟦criterion 3⟧
- [x] a probe breaking one exit path of park_issue.main turns a moved case red ⟦criterion 4⟧
- [x] test_park_issue_process.py keeps only entry-point cases, exit 0 and 2 passed through and --help printing the usage, beside the cases that also start git ⟦criterion 2⟧
