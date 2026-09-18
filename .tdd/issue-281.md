# Plan for #281 — status.sh: structural cleanup — duplicated main_working_tree, repeated event-log loop, string-spliced JSON

- [x] a shared sourced helper defines main_working_tree once, and status.sh and solvable-issues.sh both resolve the main working tree through it (first `worktree <path>` line of git's registry, even when called from a linked worktree) ⟦criterion 1⟧
- [x] run_activity and scope_totals read the event log through one shared per-line parse and one shared dollar/token sum, with status.sh's text and --json figures unchanged over a fixture log that has blank lines and usage events ⟦criterion 2⟧
