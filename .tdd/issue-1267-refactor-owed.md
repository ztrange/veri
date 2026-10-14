### The conductor's base directory is the skill commit's snapshot, pinned through run_cli: replaces 'the conductor's base directory is a snapshot of the skill commit, not the clone' in skills/tdd/scripts/tests/run-conductor.test.sh ⟦replaces-case⟧ ⟦added⟧ ⟦criterion 1⟧
- test-only | extract one helper for the "build a scratch skill dir with a `scripts/veri/run_conductor.py` symlink and load it via `importlib.util.spec_from_file_location`" block, repeated across about 6 tests including the new snapshot case (pre-existing copies outside this cycle's code)
- test-only | extract a helper for the `VERI_NEW_SKILL`/`VERI_SKILL_COMMIT`/`VERI_SKILL_CLONE`/`VERI_SKILL_REF`/`VERI_SKILL_UNPINNED` delenv loop, repeated about 8 times (mostly pre-existing)
### A resume is handed a fresh snapshot of the recorded commit, pinned through run_cli: replaces 'a resume of the run is handed a re-materialised snapshot of the recorded commit, not the clone's new HEAD' in skills/tdd/scripts/tests/run-conductor.test.sh ⟦replaces-case⟧ ⟦added⟧ ⟦criterion 1⟧
- test-only | the `cwd = tmp_path / "cwd"; cwd.mkdir()` pair repeats in two snapshot cases and could become a fixture or helper
- test-only | the `claude_reads_its_base` closures in the base-directory and resume cases share the same fake-claude dispatch preamble
### An unpinned launch hands over VERI_SKILL_UNPINNED=1, pinned through run_cli: replaces 'an unpinned launch hands the conductor VERI_SKILL_UNPINNED=1, and SKILL.md's plan-comment step names it' in skills/tdd/scripts/tests/run-conductor.test.sh ⟦replaces-case⟧ ⟦added⟧ ⟦criterion 1⟧
- test-only | none
### A launch leaves both checkouts' git status empty, pinned through run_cli: replaces 'the snapshot leaves git status --porcelain empty in the caller's checkout and in the skill clone' in skills/tdd/scripts/tests/run-conductor.test.sh ⟦replaces-case⟧ ⟦added⟧ ⟦criterion 1⟧
- test-only | the `cwd = tmp_path / "cwd"; cwd.mkdir()` pair repeats in five cases in `test_run_conductor.py` and could become a fixture
- test-only | the `claude_reads_its_base` stub (pass non-`fake-claude` calls to `subprocess.run`, record the base directories) is near-identical across the snapshot cases
