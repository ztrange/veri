# Plan for #27 — ensure-run-state-ignored.sh: target repo ignores veri run state before the first commit

- [x] on a repo with no .gitignore, creates one under which git check-ignore ignores .tdd/develop-red.log but not .tdd/issue-7.md
- [x] on a repo that already carries the rule, leaves .gitignore byte-identical and reports already present
- [ ] on a repo with an unrelated .gitignore, keeps every existing line and reports added
