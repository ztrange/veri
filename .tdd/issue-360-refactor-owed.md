### add-ledger-step.sh inserts `- [ ] <text> ⟦added⟧ ⟦criterion k⟧` after the anchor step, carrying the anchor's k, exit 0 ⟦criterion 1⟧
- extract the ` ⟦criterion k⟧` literal shared by add-ledger-step.sh:25 and criterion-finished.sh:15 into a `scripts/lib/` builder — judged below the bar and left: it would add a lib file, a `HERE` resolution and a source line into a unit-tier script to dedupe a twenty-character format string that criterion-finished.sh then interpolates into two regexes anyway
### `before` inserts several texts, in the order given, on the lines before the anchor step ⟦criterion 2⟧
- `added_steps` reads the script-level `texts` array rather than taking it as a parameter; passing it explicitly would narrow the scope, but bash array-passing costs a `shift` dance and the script is a flat script, not a library — judged not an improvement, left in place
### an anchor matching no step, or more than one, exits 2 and leaves the ledger byte-identical ⟦criterion 7⟧
- `where` is never validated — a third word silently rewrites the ledger unchanged and exits 0; the two `if [[ "$where" == before/after ]]` lines want one `case` with an `exit 2` default, which needs a triangulating test first since no case covers a bad `where`
### VERI_STEP_GROWTH unset allows 3 added steps; a value that is not a non-negative integer, set-but-empty included, exits 2 and leaves the ledger byte-identical ⟦criterion 8⟧
- `criterion_of` spells `⟦criterion ` three times over (the glob test, the `##` strip, the `printf` format) — naming it would remove the duplication, but the `printf ' %s%s⟧'` arm it forces reads worse than the literal, so I left it
### SKILL.md's Draft PR section copies the ledger's `## Owed steps` bullets into the PR body under `## Owed steps` ⟦criterion 10⟧
- extract the shared `grep -qF 'body'` probe of cases 6 and 7 into a predicate helper beside `names_the_full_gate` — left undone: it is one grep, and the two cases assert different things reaching the body
