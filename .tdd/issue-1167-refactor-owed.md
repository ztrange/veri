### A suite killed by signal N after it printed its count line makes run-suite.sh exit 128+N ⟦criterion 1⟧
- test-only | extract the repeated `subprocess.run([sys.executable, str(SCRIPTS / "veri" / "run_suite.py"), suite], stdin=subprocess.DEVNULL, capture_output=True, timeout=10).returncode` in `test_run_suite.py:332` and `:339` into one helper that runs the module as the shim does
