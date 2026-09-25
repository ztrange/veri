# Plan for #471 — A leaf launch is refused while another leaf still owns the worktree

- [x] A launch through supervise.sh under one name is refused while a stub leaf supervised under a different name is still alive in the same worktree — exit 2, no second leaf started, stderr naming the live leaf and its pid ⟦criterion 5⟧
- [x] A launch through supervise.sh is refused the same way while a stub leaf supervised under the same name is still alive in the same worktree ⟦criterion 1⟧
- [x] The record the refusal reads survives the pre-launch rm -f .tdd/<name>.exit .tdd/<name>.pid, so the launch after that rm is still refused while the first leaf lives ⟦criterion 3⟧
- [x] A record left by a supervised leaf whose process is gone does not refuse the next launch ⟦criterion 2⟧
- [x] A launch after the previous supervised leaf finished runs as today — under a different name, and a revise relaunch under the same name ⟦criterion 4⟧
- [ ] A supervised launch made from inside a live supervised leaf — verify.sh's own verify-<phase> leaf under a live verdict-<phase> wrapper — is not refused
