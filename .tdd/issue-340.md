# Plan for #340 — `make watch` reruns `make unit` on a tracked-file change (low priority)

- [x] `make -n watch` exists as its own `.PHONY` target, separate from `test`, `unit`, and `merge-gates` ⟦criterion 1⟧
- [x] A malformed `VERI_WATCH_INTERVAL` exits 2 with a diagnostic naming the variable; unset, it defaults to `1` ⟦criterion 2⟧
- [x] With an injected poll-iteration count and a fabricated file-change signal on a fixture tracked file, the watch loop reruns `make unit` exactly once per detected change and zero times between changes ⟦criterion 3⟧
- [x] One poll pass over the tracked files calls its stat wrapper exactly once whatever the number of tracked files (in-process spy), so the polling path is taken rather than the fswatch/entr fallback ⟦criterion 4⟧
- [ ] The watch loop never runs any make target besides `unit` — a fixture fails if `test`, `merge-gates` or any other target runs ⟦criterion 5⟧
- [ ] The Makefile's comment header documents `make watch` as low priority / a developer convenience, in the style of the `profile` and `docs` comments ⟦criterion 6⟧
- [ ] `watch.test.sh` is run by `make test`'s glob and is not run by `make unit` ⟦criterion 7⟧
