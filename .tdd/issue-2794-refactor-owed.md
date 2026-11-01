### fix the full-suite failure: skills/tdd/scripts/tests/py/test_shims.py — FAILED test_every_module_a_shim_execs_goes_through_the_shared_entry_point: install_links does not go through entry.run ⟦suite-repair⟧ ⟦criterion 2⟧
- drop the redundant `os.makedirs(os.path.dirname(target))` in `install_links.py`, since `os.makedirs(target)` already creates the parent directories
- drop the `try/except OSError` in `install_links.py`, since `entry.run` already turns an unexpected `OSError` into a refusal; this would change the stderr text, so it is not behavior-preserving
