### `merge-lock.sh gate --pid 1 --` (a `--` with no command after it) exits 2, writes the gate usage line to stderr, prints no `Traceback`, and creates no `.tdd/` ⟦criterion 1⟧
- test-only | the two test_2374 cases repeat the same init/run/assert body; they could become one parametrized case over the argv tails `["--pid","1"]` and `["--pid","1","--"]`
