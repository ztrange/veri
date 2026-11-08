## What happened

A `projects/dashboard/` case that passes under the dashboard's own runner (`make -C projects/dashboard test`) fails under veri's root `make test TESTS=<path>`. That root command is what veri's leaves and verifiers run, and it goes through `skills/tdd/scripts/veri/pytest_leg.py` with veri's case-size rules (CLAUDE.md "Pytest case sizes"): an unmarked case refuses `git` and `python3` subprocesses. Dashboard cases start `projects/dashboard/serve.py` as a real process and carry no `@pytest.mark.process` mark, so the guard refuses them.

Evidence: run #3265 (PRD 014.7a local dashboard) bailed `revise-exhausted` on step 13. Its green passed `make -C projects/dashboard test` (18 passed); verify-green then failed the same case under the root `make test`'s small-case guard.

#3334 (closed, PR #3337) made `affected-suites.sh` print `projects/dashboard/tests/...` paths for dashboard changes (`skills/tdd/scripts/veri/affected_suites.py:227-228`) but wired no runner for them: those paths still flow into root `make test TESTS=`.

Dispatch sites (where a test path reaches veri's pytest leg):
- `Makefile:21` `PY_TESTS := $(call py_tests,...)` keeps each `TESTS` entry containing `.py`; `Makefile:20` `PY_REFUSED` exits 2 on the rest.
- `Makefile:108` runs `skills/tdd/scripts/veri/pytest_leg.py --subset ... $(PY_TESTS)`, handing every path, dashboard ones included, to veri's runner.
- `skills/tdd/scripts/veri/pytest_leg.py:280` `main(argv)` (`--subset` parsed at `:320-321`) is the single entry that applies the case-size rules.

`projects/dashboard/` exists only on branch `tdd/3265-prd-014-7a-a-local-dashboard` (`git ls-tree origin/main projects/` is empty); its `projects/dashboard/Makefile` `test` target runs `python3 -m pytest -q tests`.

Fix chosen: a test path under `projects/dashboard/` runs under the dashboard's own runner, wherever veri runs affected suites or `make test TESTS=...` (either root `make test` or the leg delegating such paths to `make -C projects/dashboard test`).

Rejected alternative: requiring every dashboard case that starts `serve.py` to carry a process mark. That imposes veri's convention on a separate project, and every Red leaf would have to remember it.

This unblocks #3265 (PRD 014.7a), which bailed on it; it is not listed under Blocked by because #3265 is a PRD whose issue must not wait on this one by that mechanism.

## Acceptance criteria

- [ ] `make test TESTS=projects/dashboard/tests/<case>.py` runs that case under `make -C projects/dashboard test` semantics, not veri's small-case guard: a dashboard case that starts `serve.py` with no process mark passes (pinned by a case).
- [ ] A `TESTS` list mixing a `projects/dashboard/` path and a veri path runs each under its own runner, and exits non-zero if either fails (pinned by a case).
- [ ] A failing dashboard case run through `make test TESTS=projects/dashboard/...` exits 1, and a runner that cannot start (dashboard Makefile or interpreter missing) exits 2, per the exit-code contract (pinned by a case).
- [ ] Veri paths keep veri's rules: an unmarked veri case that spawns `git`/`python3` still refuses (pinned by a case).
- [ ] Go-red: with the dashboard delegation removed, the first criterion's case goes red.

## Plan notes

The step that routes projects/dashboard/ paths to the dashboard's own runner adds the routing only. It must not propagate that runner's exit status (no `|| fail=1`) and must add no exit guard (no `[ -f projects/dashboard/Makefile ] || exit 2`). On the before-state a dashboard case already makes `make test` exit nonzero via the small-case guard, so a case requiring either one cannot go red, and a verifier asking for one loops. Exit propagation is the later Pin step's, against the mutant of dropping `|| fail=1`.

## Blocked by

None.

Test command: make test


