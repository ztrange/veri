# Plan for #3983 — PRD 021.10: a stalled `gh` call ends with no answer

- [x] `run_gh`, `gh_probe`, `rate_limit_reset` and `gh_pr_ready`'s `git ls-remote`, each against a faked process that never returns, end after `VERI_GH_TIMEOUT` seconds with a non-zero result (or no reset) whose stderr names the command and the limit; a small case in `tests/py/unit/test_github.py` ⟦criterion 1⟧
- [x] `pr-ready.sh` with `VERI_GH_TIMEOUT` set to a value that is not a whole number of at least 1 exits 2 with one stderr line naming `VERI_GH_TIMEOUT`, starting no `gh`; a small case through `run_cli` in `tests/py/unit/test_github.py` ⟦criterion 2⟧
- [x] `wait-ci.sh`, its every PR read timing out and the clock past its deadline, exits 2 naming the PR, never 3; a small case through `run_cli` in `tests/py/unit/test_wait_ci.py` ⟦criterion 3⟧
- [ ] the `run_gh` entry of `skills/tdd/scripts/veri/README.md` states the bound and what a timed-out call returns ⟦criterion 4⟧
