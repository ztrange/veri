# Plan for #4833 — run-step.sh --from green-half skips develop-green after a successful reroute.sh: stale green-half-rejected-wait record

- [x] after a verify-green REJECT left `.tdd/issue-<n>-green-half-rejected-wait` and `.tdd/verdict-green.exit`, a successful `reroute.sh <n> <report>` (exit 0), run on its own and not through `run-step.sh`, removes both files ⟦criterion 1⟧
- [x] after a verify-green REJECT and a successful `reroute.sh <n> <report>` run on its own, `run-step.sh <n> --from green-half` calls `green-half.sh <n>` and never `revise.sh <n> green` ⟦criterion 1⟧
- [ ] fix the weak-assertion case skills/tdd/scripts/tests/py/unit/test_reroute.py::test_a_wait_record_naming_another_step_is_dropped_and_the_route_runs_again_4434: it never asserts `.tdd/issue-12-reroute-wait` is gone, so a `pending` that ignored another step's record but left it on disk would pass; edit only that case, no production code ⟦test-quality⟧ ⟦diff-checked⟧ ⟦added⟧ ⟦criterion 1⟧
