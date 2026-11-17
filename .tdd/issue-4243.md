# Plan for #4243 — The leaf-kills-its-own-pid process case passes whenever a leaf can kill a pid it started, whether or not its background sleep was quick to start

- [ ] the case's stub waits, bounded, until its background `sleep 30` is the running sleep and alive before it kills it, and a sleep that never starts fails the case with its own message naming what failed to start and its exit code ⟦criterion 2⟧
- [ ] a process case's `sleep` shim reaches the real sleep in an environment that dropped `REAL_SLEEP` and `PUSH_BACKOFF_LOG` (a leaf's allow-list does), so a leaf's background `sleep` starts ⟦criterion 1⟧
