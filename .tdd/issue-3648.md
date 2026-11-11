# Plan for #3648 — role-state.sh with --lane and no verb prints usage and exits 2 instead of an IndexError

- [ ] `role-state.sh <role> --lane <lane>` with no verb after the lane prints the usage line on stderr and exits 2, not an IndexError traceback with exit 1; pinned by a small in-process case (run_cli) that is red on the current code ⟦criterion 1⟧
- [ ] `role-state.sh <role>` with no verb and no `--lane` still prints the usage line on stderr and exits 2; pinned by a small in-process case (run_cli) ⟦criterion 2⟧
