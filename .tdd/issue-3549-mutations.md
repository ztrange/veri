file 21
skills/tdd/SCRIPTS.md
old 15
- `$S/status.sh
new 16
- `$S/statusX.sh
context 689
- `$S/status.sh [--json] [--scope <name>] [--watch [seconds]] | --report` — render every run under the main working tree. `--report` (alone) prints the `/vstatus` report from local files only, with no `gh` call: the sections Landed, Running, Queue and Waiting, the queue read from the cached snapshot `.tdd/report-cache.json`. When that snapshot is stale (older than `VERI_SNAPSHOT_MAX_AGE` seconds, default 60) and no refresh is running, it starts `report-cache.sh refresh` detached (its own session, no stdin, stdout or stderr), so a caller capturing the report never waits for it. **Exit 0** printed, **2** an unknown option (a usage line on stderr), **3** no runs (without `--report`).
command 72
make test TESTS=skills/tdd/scripts/tests/py/unit/test_scripts_md_rows.py

