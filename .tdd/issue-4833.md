# Plan for #4833 — run-step.sh --from green-half skips develop-green after a successful reroute.sh: stale green-half-rejected-wait record

- [x] after a verify-green REJECT left `.tdd/issue-<n>-green-half-rejected-wait` and `.tdd/verdict-green.exit`, a successful `reroute.sh <n> <report>` (exit 0), run on its own and not through `run-step.sh`, removes both files ⟦criterion 1⟧
- [ ] after a verify-green REJECT and a successful `reroute.sh <n> <report>` run on its own, `run-step.sh <n> --from green-half` calls `green-half.sh <n>` and never `revise.sh <n> green` ⟦criterion 1⟧
