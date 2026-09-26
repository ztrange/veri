### SKILL.md runs each cost check only once the leaf has exited and its `usage` event has been harvested
- fold the `if [[ ! -r "$skill_path" ]] … else` guard repeated in every case of skill-revise-exhausted.test.sh into one helper (the pattern predates this cycle, so out of scope here)
### SKILL.md states that `step-cost.sh` exit 3 (no leaf of this step has reported yet) is not a crossing ⟦criterion 4⟧
- the `if [[ ! -r "$skill_path" ]]` fail-closed guard repeated across every case of skill-revise-exhausted.test.sh could be one helper — most of those cases predate this cycle, so it is out of this step's bounds
### SKILL.md's crossing branch builds the `over-budget` prompt, launches its leaf through `supervise.sh` the way the exhausted leaf is launched, and reads its answer with `exhausted-outcome.sh`, never by eye ⟦criterion 5⟧
- revise_prose_sentences and cost_check_sentences in skill-revise-exhausted.test.sh repeat the same awk sentence-splitter, which could become one shared `sentences` helper — outside scope, because an earlier step wrote both copies, not this cycle
### The over-budget exit 0 branch restores the tree (`git reset --hard HEAD`, `git clean -f -- <test-path>`) before growing the plan, grows it in one `add-ledger-step.sh instead-of` call, and commits the plan before the run continues ⟦criterion 6⟧
- SKILL.md's over-budget split command block (L827-835) repeats the revise-exhausted split block (L1485-1493) word for word; it can't be replaced with a pointer while skill-revise-exhausted.test.sh requires the commands inside the cost check's section
### The *Bailing* list's `step-too-big` entry names all three splits that lead to it — a Green leaf's `SPLIT:`, the revise-exhausted split and the over-budget split ⟦added⟧ ⟦criterion 7⟧
- `step_too_big_cause` and `bailing_causes` each repeat the same awk scan of the `## Bailing` section; one helper taking a start pattern would remove the repeat
