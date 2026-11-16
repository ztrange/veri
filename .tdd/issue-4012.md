# Plan for #4012 — PRD 024.6: revise-green gets its own model knob

- [ ] `VERI_MODEL_REVISE_GREEN` is a text entry of `tunables.TUNABLES` defaulting to empty ⟦criterion 1⟧
- [ ] `leaf-model.sh revise-green` and `revise-green-<k>` print `VERI_MODEL_REVISE_GREEN` when set and not blank, over every other model knob, while every other leaf, and every leaf with it unset or blank, resolves as before ⟦criterion 2⟧ ⟦criterion 3⟧ ⟦criterion 4⟧
- [ ] the report's `Models requested:` line names `VERI_MODEL_REVISE_GREEN` with its value or `unset`, and the "dollars are not comparable" sentence names it beside the four other knobs ⟦criterion 5⟧
- [ ] `metrics.sh <n>` prints `#### Revise-green, by model` with one row per answering model: leaves, and the PASS and REJECT of the first green verdict of the same step after each; absent when no revise-green leaf ran ⟦criterion 6⟧
