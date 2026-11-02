# Plan for #2878 — An unparseable WRONG_TEST report routes revise, so the step's own Red is never repaired

- [ ] A `WRONG_TEST: none` report prints `revise` and exits 3, pinned by a small `run_cli` case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py; the existing case test_main_1736_prints_revise_when_a_real_case_is_named_only_on_lines_other_than_wrong_test stays green ⟦criterion 2⟧
- [ ] Once the step's event log already holds a `reroute` event, a `WRONG_TEST:` report naming its case in bare prose prints `revise` and exits 3, so a later route cannot loop with no budget, pinned by a small `run_cli` case ⟦criterion 3⟧
- [ ] A `WRONG_TEST:` report naming another existing case in backticks routes exactly as today (`red <case>`, exit 0), pinned by a small `run_cli` case ⟦criterion 4⟧
- [ ] A `WRONG_TEST:` report naming another existing case in double quotes routes exactly as today (`red <case>`, exit 0), pinned by a small `run_cli` case ⟦criterion 4⟧
- [ ] A `WRONG_TEST:` report naming another existing case in curly quotes routes exactly as today (`red <case>`, exit 0), pinned by a small `run_cli` case ⟦criterion 4⟧
- [ ] A `WRONG_TEST:` report naming another existing case in the bare `test_` form routes exactly as today (`red <case>`, exit 0), pinned by a small `run_cli` case ⟦criterion 4⟧
- [ ] A `WRONG_TEST:` report naming another existing Go case in the bare `Test` form routes exactly as today (`red <case>`, exit 0), pinned by a small `run_cli` case ⟦criterion 4⟧
- [ ] A `WRONG_TEST:` report naming another existing case in the `suite › case` form routes exactly as today (`red <case>`, exit 0), pinned by a small `run_cli` case ⟦criterion 4⟧
- [ ] A report carrying no `WRONG_TEST:` line at all prints `revise` and exits 3, pinned by a small `run_cli` case ⟦criterion 5⟧
- [ ] A `WRONG_TEST:` report that names its case in bare prose (no backticks, no quotes, no `test_`/`Test` prefix, no `suite › case` form) on a step not yet rerouted does not print `revise`: it prints `repair <the step's own case>` and exits 0, so the existing `red-repair` route repairs the step's own Red, asserted by a small `run_cli` case ⟦criterion 1⟧
