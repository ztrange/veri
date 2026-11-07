# Plan for #3180 — Leaves get the full toolset: run_leaf.py passes a default --tools list

- [ ] With `VERI_LEAF_TOOLS` unset, `run_leaf.py` launches `claude` with `--tools` followed by a default comma-separated list naming at least Bash, Read, Edit, Write, Grep and Glob (the tools the leaf prompts use), unless the caller's own arguments already carry `--tools`; pinned by a small in-process case on the launched argv, and the existing argv cases in `test_run_leaf.py` and `test_supervise.py` stay unchanged and green ⟦criterion 1⟧
- [ ] With `VERI_LEAF_TOOLS` set to an explicit value (a list, or the empty string), `run_leaf.py` launches `claude` with `--tools` followed by exactly that value and never the default list; pinned by a small in-process case on the launched argv ⟦criterion 1⟧
