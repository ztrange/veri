# Plan for #634 — status.sh runs as a Python module behind its sh shim, in the veri/ package the lib/*.py modules move into

- [ ] run-suite.sh, given a tests/py/test_*.py path, runs that file under pytest and exits 0 when every case is green and 1 when a case fails ⟦criterion 7⟧
- [ ] run-suite.sh, given a tests/py/test_*.py path, exits 2 with no answer when pytest cannot be imported or the named file does not exist ⟦criterion 7⟧
- [ ] affected-suites.sh, given a touched veri/<module>.py, prints tests/py/test_<module>.py when it exists and the bash suite of the entry point over that module (underscore in the module name read as a hyphen in the script's), without the widening notice ⟦criterion 6⟧
- [ ] affected-suites.sh, given a touched tests/py/test_<module>.py, prints that file without the widening notice ⟦criterion 6⟧
- [ ] no Python module is left under scripts/lib/: event_log, blocked_by, json_documents and leaf_log are modules of the scripts/veri/ package, and every script that imported one from lib/ finds it there with its suite passing unmodified ⟦criterion 5⟧
- [ ] status.sh is a /bin/sh shim over veri/status.py holding no Python source, calling python3 once per invocation, and tests/status.test.sh passes unmodified against it, committed before any change to that suite ⟦criterion 1⟧
- [ ] status.sh, run through a symlink to the skill directory and from another working directory, answers as it does when run in place ⟦criterion 2⟧
- [ ] tests/py/test_status.py asserts in-process, importing veri.status and mocking subprocess, the clock and the recorder, what each tests/status.test.sh case outside the ADR 0027 survival rule and floor asserts ⟦criterion 3⟧
- [ ] tests/status.test.sh keeps only the ADR 0027 survivors and the floor — one case per exit code status.sh uses, its bad-argument stderr text, the symlink case — the rest replaced by tests/py/test_status.py ⟦criterion 3⟧
- [ ] a guard suite fails, naming <script>:<line>, when a script whose module exists under veri/ holds Python source (a python3 -c string or a heredoc fed to python3), proven red against a planted offender ⟦criterion 4⟧
- [ ] run-conductor.sh exits 2, naming the Python 3.12 floor and the version found, when the python3 on PATH is older than 3.12 ⟦criterion 8⟧
- [ ] leaf-launchable.sh exits 2, naming the Python 3.12 floor and the version found, when the python3 on PATH is older than 3.12 ⟦criterion 8⟧
- [ ] CLAUDE.md records the shim convention (a ported script's .sh entry point is a /bin/sh shim over its veri/ module, Bash holding no Python source) and that a ported script's tests live in tests/py/test_<module>.py ⟦criterion 9⟧
