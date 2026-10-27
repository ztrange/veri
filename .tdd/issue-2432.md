# Plan for #2432 — test_worktree_setup_process.py's five shim calls go through one helper

- [x] test_worktree_setup_process.py gains one helper that runs the worktree-setup shim, and every case that ran the shim through subprocess.run directly calls that helper instead; no case calls subprocess.run on the shim directly, every case keeps its name and asserts exactly what it asserts today, the test file is the only file changed (no production change), and the fast tier and the affected suites stay green ⟦diff-checked⟧ ⟦criterion 1⟧
