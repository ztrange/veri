# Plan for #4332 — A run's metrics commit, pushed after the PR is ready, re-runs the full gates CI on a records-only change

- [x] `pr-ready-wait.sh` marks `done`, commits the metrics and pushes them before `pr-ready.sh`, and `pr-finish.sh` then makes no commit, no push and no second `wait-ci.sh` ⟦criterion 1⟧
- [ ] under `ci`, every `⟦full-suite⟧` line and its issue criterion are ticked before readying, as owed to CI, with no `.tdd/wait-ci.err` read ⟦criterion 1⟧
- [ ] `metrics.sh`'s report states that it leaves out the CI wait and `pr-finish.sh` ⟦criterion 1⟧
- [ ] with every `⟦full-suite⟧` line ticked, a red first `wait-ci.sh` still stops `pr-ready-wait.sh` with exit 1, and a resumed call still runs `wait-ci.sh` on the head ⟦criterion 2⟧
- [ ] a `has no checks` wait after the pre-readying ticks still settles `no_checks=1`, `wait-ci.sh`'s verdict unchanged ⟦criterion 3⟧
- [ ] DRAFT-PR.md and SCRIPTS.md describe the new order, their rows edited and regraded, `prose-owed.sh` exit 0 ⟦skill-edit⟧ ⟦criterion 4⟧
- [ ] the full suite is green ⟦full-suite⟧
