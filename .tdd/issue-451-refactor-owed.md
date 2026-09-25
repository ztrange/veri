### SKILL.md runs each cost check only once the leaf has exited and its `usage` event has been harvested
- fold the `if [[ ! -r "$skill_path" ]] … else` guard repeated in every case of skill-revise-exhausted.test.sh into one helper (the pattern predates this cycle, so out of scope here)
### SKILL.md states that `step-cost.sh` exit 3 (no leaf of this step has reported yet) is not a crossing ⟦criterion 4⟧
- the `if [[ ! -r "$skill_path" ]]` fail-closed guard repeated across every case of skill-revise-exhausted.test.sh could be one helper — most of those cases predate this cycle, so it is out of this step's bounds
### SKILL.md's crossing branch builds the `over-budget` prompt, launches its leaf through `supervise.sh` the way the exhausted leaf is launched, and reads its answer with `exhausted-outcome.sh`, never by eye ⟦criterion 5⟧
- revise_prose_sentences and cost_check_sentences in skill-revise-exhausted.test.sh repeat the same awk sentence-splitter, which could become one shared `sentences` helper — outside scope, because an earlier step wrote both copies, not this cycle
