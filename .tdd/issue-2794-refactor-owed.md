### fix the full-suite failure: skills/tdd/scripts/tests/py/test_shims.py — FAILED test_every_module_a_shim_execs_goes_through_the_shared_entry_point: install_links does not go through entry.run ⟦suite-repair⟧ ⟦criterion 2⟧
- drop the redundant `os.makedirs(os.path.dirname(target))` in `install_links.py`, since `os.makedirs(target)` already creates the parent directories
- drop the `try/except OSError` in `install_links.py`, since `entry.run` already turns an unexpected `OSError` into a refusal; this would change the stderr text, so it is not behavior-preserving
### After install-links.sh, .git/info/exclude of the common git directory lists each link's path and git status is clean in the target repository, pinned by a case in test_install_links_process.py carrying a process mark for git ⟦criterion 5⟧
- hoist the `_veri_skills()` call out of the `for name in LINKED` loop, since it runs git once per link
### A second run of install-links.sh changes nothing, links and exclude file byte for byte, and exits 0, pinned by a case in test_install_links_process.py carrying a process mark for git ⟦criterion 6⟧
- drop the redundant first `os.makedirs(os.path.dirname(target))` in `install_links.py`, since `os.makedirs(target)` already creates the parent
not-done | transform-rejected | drop the redundant `os.makedirs(os.path.dirname(target))` in `install_links.py`, since `os.makedirs(target)` already creates the parent directories
applied | 94ce3debed13dcaf7b66de598d2436483174bbed | drop the `try/except OSError` in `install_links.py`, since `entry.run` already turns an unexpected `OSError` into a refusal; this would change the stderr text, so it is not behavior-preserving	refactor: drop install_links' try/except OSError, entry.run already refuses (#2794)
applied | a4e6aa3f2c0e46b5e454f6597ae8d3385c471233 | hoist the `_veri_skills()` call out of the `for name in LINKED` loop, since it runs git once per link	chore: record the structural pass's applied candidate (#2794)
