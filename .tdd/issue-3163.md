# Plan for #3163 — vmerge: keep the merge lock's owner token where every call can read it

- [x] skills/vmerge/SKILL.md keeps the owner token in `$(git rev-parse --git-common-dir)/veri-merge-<pr>.token`, written at `take`, read by every later `gate` and `release` call, removed after the release, never held only in a shell variable (M18) ⟦skill-edit⟧ ⟦criterion 1⟧
- [x] skills/vmerge/SKILL.md says a lost or unreadable owner token stops the merge and is reported to the human, and the merge never runs `merge-lock.sh release --force` (M19) ⟦skill-edit⟧ ⟦criterion 2⟧
- [x] skills/vmerge/SKILL.md orders the lock release before the worktree removal, or makes the release read nothing from the worktree; the token file lives in no worktree (M20) ⟦skill-edit⟧ ⟦criterion 3⟧
- [x] fix the full-suite failure: skills/tdd/scripts/tests/py/test_prd_016_tracked_names_process.py — FAILED test_no_tracked_file_outside_specs_and_tdd_contains_veri_dash_a_renamed_skill_name: skills/vmerge/REQUIREMENTS.md and skills/vmerge/SKILL.md name the token file `veri-merge-<pr>.token`, which the renamed-skill-name guard flags ⟦suite-repair⟧ ⟦criterion 3⟧ ⟂ refactor pending
