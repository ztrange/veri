# Plan for #1605 — rebase-onto-default.sh exits 2 with nothing on stderr on four of its seven refusals

- [ ] When `git fetch -q origin` fails, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the failed fetch of origin (a small in-process case with git faked; no production change beyond the reason line) ⟦criterion 1⟧
- [ ] When `git ls-remote origin refs/heads/<default>` fails after a successful fetch, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the failed ls-remote of the default branch (a small in-process case with git faked) ⟦criterion 1⟧
- [ ] When `origin/<default>` after the fetch is not the sha `ls-remote` reports, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the stale remote-tracking ref (a small in-process case with git faked) ⟦criterion 1⟧
- [ ] When `git rebase -q <onto>` fails while a rebase was already in progress before it ran, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the rebase already in progress (a small in-process case with git faked) ⟦criterion 1⟧
- [ ] When `git rebase -q <onto>` fails without leaving a rebase in progress, `rebase-onto-default.sh` exits 2 and prints exactly one line on stderr naming the rebase refused without a conflict (a small in-process case with git faked) ⟦criterion 1⟧
- [ ] The seven exit-2 refusals of `rebase-onto-default.sh` each print a stderr reason line that differs from every other refusal's line, pinned by one small case driving all seven paths and comparing their stderr lines ⟦criterion 1⟧
