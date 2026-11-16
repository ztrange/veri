# Plan for #3930 — PRD 023.18: pin_fast_tier's logic is tested once, in-process, and its shim once

- [x] every case of test_pin_fast_tier_process.py that starts only pin-fast-tier.sh and its fast command runs in-process through run_cli in unit/test_pin_fast_tier.py, with the same argv and cwd and the same asserted exit code, stdout, stderr and reason file, the fast command answered through fake_processes with the output its stub printed ⟦criterion 1⟧
- [x] every moved case is small: no process or tree_audit mark, and fast_tier_guard names none ⟦criterion 3⟧
- [x] a probe breaking one exit path of pin_fast_tier.main turns a moved case red ⟦criterion 4⟧
- [ ] test_pin_fast_tier_process.py keeps only entry-point cases, exit 0, 1 and 2 passed through and --help printing the usage, beside the 2 cases that also start git or a leaf ⟦criterion 2⟧
