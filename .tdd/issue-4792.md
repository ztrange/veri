# Plan for #4792 — A resumed run that finishes again writes no done event, so run-finished.sh reads it as stale

- [x] A run whose journal ends `done`, then `resume`, further work and a later `comment` event of `kind=done` (the second ✅ Done comment), with no live conductor, reads as finished: `run-finished.sh <n>` exits 0 and `status.sh --json` reports the run `done` with the first `done` event's PR, not `stale` ⟦criterion 1⟧
- [x] A run whose journal ends `done`, then `resume` and further work with no later `comment` event of `kind=done`, and no live conductor, still reads as not finished: `run-finished.sh <n>` prints `not-done stale` and exits 1 ⟦criterion 1⟧
- [x] A resumed run that re-posts its Done comment after two earlier `done` events reports the latest `done` event's PR
