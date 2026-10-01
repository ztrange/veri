# Plan for #549 — wait-ci.sh's bound is twice the mean of the last 5 CI runs, capped at 10 min, not a fixed 540 s

The issue predates #544's landing: `wait-ci.sh` now takes `<pr-url> [slice-seconds] [total-seconds] [head-sha]`. The issue's "bound" is the total deadline across calls (`total-seconds`); its "one call never sleeps longer than 540 s" is the slice. An omitted or empty `total-seconds` is "no max-seconds argument".

- [x] with no `total-seconds` argument (omitted or empty), `wait-ci.sh`'s total bound is 2 × the mean wall time (`updatedAt − startedAt`) of the 5 most recent runs of the CI workflow whose conclusion is `success` or `failure`, read through `gh run list`, skipped and cancelled runs not counted — the deadline recorded in `.tdd/ci-deadline-<sha>` is that many seconds after the first call ⟦criterion 1⟧ ⟂ refactor pending
- [ ] the computed total bound is never more than 600 s, however slow the last 5 runs were ⟦criterion 1⟧
- [ ] when fewer than 5 success/failure CI runs exist, the total bound falls back to 540 s and `wait-ci.sh` says so on stderr, naming that fewer than 5 runs were found ⟦criterion 2⟧
- [ ] when `gh run list` fails, the total bound falls back to 540 s and `wait-ci.sh` says so on stderr, naming that `gh` could not answer ⟦criterion 2⟧
- [ ] one `wait-ci.sh` call's slice is never longer than 540 s: a `slice-seconds` argument above 540 is capped to 540, so a call still returns exit 3 within 540 s while a longer total bound spans calls ⟦criterion 3⟧
- [ ] an explicit `total-seconds` argument overrides the computed bound (no `gh run list` reading needed), but a value above 600 is capped at 600 ⟦criterion 4⟧
- [ ] `workflow-timeouts.test.sh` fails a workflow job that declares a `timeout-minutes` above 10, naming the job, and every job in `.github/workflows/ci.yml` passes it (the `gates` job's 8 is not raised) ⟦criterion 5⟧
- [ ] the Draft PR step in `skills/tdd/SKILL.md` calls `wait-ci.sh` without a fixed total (no `1800`) and its prose states the bound's rule — twice the mean of the last 5 completed CI runs, capped at 10 minutes, 540 s fallback — not a number standing for it ⟦criterion 6⟧
