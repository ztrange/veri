# Plan for #4457 — PRD 036.11: a cap the human sets bounds T

- [x] The hermetic fixture points `VERI_TEST_CAP_FILE` into the case's tmp_path, and the process cases that hand a child make the case's ceiling record hand it the case's cap file too, so no case reads the machine's `~/.veri-test-cap`
- [x] CAP1, CAP2: a leg reads the cap from line 1 of `VERI_TEST_CAP_FILE` when it is a whole number of at least 2; T is min(C0, the cap): a cap of 4 beside a record of 8 gives a full leg alone 4, a cap of 12 changes nothing, no cap file says nothing and the leg writes no cap file. Pinned by small in-process cases in test_pytest_leg.py ⟦criterion 1⟧ ⟦criterion 2⟧
- [x] CAP3: a cap file that cannot be read (a directory) or whose line 1 is not a whole number of at least 2 sets no cap and is one stderr line naming the file; the leg runs on C0, exit 0. Pinned by small in-process cases ⟦criterion 3⟧
- [x] CAP4: with the cap below C0, the wait line names the cap file as T's source beside C0 and C0's source. Pinned by a small in-process case ⟦criterion 4⟧
- [x] CAP7: with `VERI_PYTEST_WORKERS` exported the leg never opens the cap file, and a bad one says nothing. Pinned by a small in-process case, watched red by moving the read ahead of the override ⟦criterion 7⟧
- [x] CAP5: with a cap, `test-ceiling.sh` ramps 2, 4, … up to the least of the logical cores, `--max` and the cap, an odd top included, and its exit-0 stdout line names which bounded the ramp when no step timed out. Pinned by in-process cases in test_ceiling.py ⟦criterion 5⟧
- [ ] CAP6: a cap file `test-ceiling.sh` cannot use is one stderr line and the ramp runs as with no cap. Pinned by in-process cases ⟦criterion 6⟧
- [ ] CAP8: CLAUDE.md's Testing idiom and `make ceiling` row, and SCRIPTS.md's `test-ceiling.sh` entry state the cap (rows CAP8, CAP8b), with the leg's and test-ceiling.sh's usage headers and veri/README.md's tunables table, regraded ⟦criterion 8⟧
