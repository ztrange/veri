### The path-setup case in test_conftest.py (and every other tests/py case) gives the same outcome when pytest is started from skills/tdd/scripts/ with a relative test path as from the repository root, though tests/py lands first on sys.path there ⟦added⟧ ⟦criterion 4⟧
- test-only | test_conftest.py:162 and :177 each re-derive `pathlib.Path(__file__).resolve().parents[2]`, which `conftest.SCRIPTS` already holds. The same line is at :15.
- test-only | The two `started_from` helpers at :165 and :180 are the same `subprocess.run([sys.executable, "-m", "pytest", ...], cwd=cwd, capture_output=True, text=True).returncode` call with different arguments. They could share one helper.
### A pytest case that starts a process running a bash suite under tests/ (a `*.test.sh` file there as the script bash or sh runs, or as the executable itself) fails, naming the case and the command, through conftest.py natively ⟦criterion 1⟧
- out-of-scope | factor the "path is ROOT or under it" test, repeated in hermetic_environment and unmarked_case_lists_no_repository_directory, into one helper (both lines predate this cycle)
### A pytest case that starts pytest as a process (the pytest executable, `python3 -m pytest`, or veri/pytest_leg.py) fails, naming the case and the command ⟦criterion 1⟧
- test-only | the `started_from` helpers in the two cwd cases in `test_conftest.py` repeat the subprocess call
