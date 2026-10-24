# Plan for #2308 — the conductor's model is a knob, VERI_MODEL_CONDUCTOR, defaulting to Opus

- [x] run-conductor.sh <issue> launches claude with `--model <value>` when VERI_MODEL_CONDUCTOR is set to a value (e.g. sonnet), pinned by a small in-process case on the launched argv ⟦criterion 1⟧
- [x] run-conductor.sh <issue> launches claude with `--model opus` when VERI_MODEL_CONDUCTOR is set but empty, and when it is unset, pinned by one case per state on the launched argv ⟦criterion 1⟧
- [x] run-conductor.sh records, at launch, the model it hands the conductor's `--model` (opus by default, else VERI_MODEL_CONDUCTOR's value) in the run's `.tdd/issue-<n>-conductor-model` beside its `issue-<n>-tmpdir-skill-commit` record, pinned by a case over a launch with VERI_MODEL_CONDUCTOR set ⟦criterion 2⟧
- [ ] metrics.sh <n> names the conductor's model on its "Conductor own spending" line, read from the run's `.tdd/issue-<n>-conductor-model` record, pinned by a case over a run recorded with a non-default conductor model ⟦criterion 2⟧
- [ ] run-conductor.sh's header comment and CLAUDE.md's model-knobs invariant name VERI_MODEL_CONDUCTOR and its Opus default, and no text in either says no variable chooses the conductor's model ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] skills/tdd/SKILL.md's launch passage (the `run-conductor.sh` skill-snapshot paragraph) names VERI_MODEL_CONDUCTOR and its Opus default, and no text there says no variable chooses the conductor's model ⟦skill-edit⟧ ⟦criterion 3⟧
