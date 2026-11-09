# Plan for #3436 — VERI_BASELINE_FULL_TIER=reuse is prose-only: the conductor ran the full tier in preflight

- [x] A new script `baseline-full-tier.sh <issue> <full-tier-command>` (logic in `veri/baseline_full_tier.py`, a `/bin/sh` shim, cases in `tests/py/unit/test_baseline_full_tier.py` driven in-process with `run_cli`), called with no argument, exits 2 with a usage line naming it on stderr ⟦criterion 1⟧
- [x] `baseline-full-tier.sh <issue> <full-tier-command>` prints `run` and exits 0 when `VERI_BASELINE_FULL_TIER` is unset ⟦criterion 1⟧
- [x] Given `VERI_BASELINE_FULL_TIER=reuse` and a time recorded through `full-tier-time.sh --record <seconds> <command>` for the full-tier command it is given, `baseline-full-tier.sh` prints `reuse <seconds>` and exits 0 ⟦criterion 1⟧
- [x] fix the full-suite failure: skills/tdd/scripts/tests/py/unit/test_tunable_reads.py — FAILED test_no_module_but_the_reader_and_the_exempt_ones_reads_a_veri_name_from_the_environment (veri/baseline_full_tier.py:15 reads a VERI_ name directly) ⟦suite-repair⟧ ⟦criterion 1⟧ ⟂ refactor pending
- [ ] Given `VERI_BASELINE_FULL_TIER=reuse` and no recorded time for the full-tier command it is given, `baseline-full-tier.sh` prints `run` and exits 0 ⟦criterion 1⟧
- [ ] A fresh `run-conductor.sh <n>` launch pins the launch's `VERI_BASELINE_FULL_TIER` value per run, writing it to `.tdd/issue-<n>-baseline-full-tier` beside `.tdd/issue-<n>-skip-verify` ⟦criterion 2⟧
- [ ] A resumed `run-conductor.sh <n>` launch (skill commit recorded, `VERI_NEW_SKILL` not 1) leaves `.tdd/issue-<n>-baseline-full-tier` as the first launch wrote it, even when its own `VERI_BASELINE_FULL_TIER` differs ⟦criterion 2⟧
- [ ] `baseline-full-tier.sh <issue> <command>` takes the run's pinned value from `.tdd/issue-<issue>-baseline-full-tier` (in the main checkout's `.tdd/`, where `run-conductor.sh` writes it) in preference to its own environment: a pinned `reuse` with a recorded time prints `reuse <seconds>` while `VERI_BASELINE_FULL_TIER` is unset ⟦criterion 2⟧
- [ ] skills/tdd/SCRIPTS.md catalogues `$S/baseline-full-tier.sh <issue> <full-tier-command>` (its output `reuse <seconds>` or `run`, the pinned per-run value it reads, its exit codes) with an SC row in REQUIREMENTS.md ⟦skill-edit⟧
- [ ] skills/tdd/PREFLIGHT.md step 3 tells the conductor to run `$S/baseline-full-tier.sh` and follow its output, graded by PF35 as the issue rewords it ⟦skill-edit⟧ ⟦criterion 3⟧
- [ ] Guard's go-red: with the script's `reuse` branch broken, the case of criterion 1 goes red ⟦human-owed⟧ ⟦criterion 4⟧
