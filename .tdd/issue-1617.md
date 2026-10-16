# Plan for #1617 — unreplaced-cases.sh reports a case as unreplaced when the Red report names it without the step's bash escapes

- [x] unreplaced-cases.sh counts a REPLACES: line as replacing a step's case when the reported name equals the step's name with every backslash escape removed (a `\` followed by `` ` ``, `"`, `$` or `\`), e.g. step name ``\`### 🔴 Red\` `` and report name `` `### 🔴 Red` ``, and exits 0 when that was the only case ⟦criterion 1⟧
- [x] unreplaced-cases.sh still counts a REPLACES: line whose name keeps the step's backslash escapes exactly as a replacement, exiting 0 ⟦criterion 2⟧
- [x] unreplaced-cases.sh still prints a step's case and exits 1 when the only REPLACES: line's name, with backslash escapes removed, differs from the step's name with backslash escapes removed ⟦criterion 3⟧
- [x] replaces-case-survivors.sh still prints a step case named with backslash escapes when its suite's source still holds that case spelled with those same escapes ⟦criterion 4⟧
- [ ] unreplaced-cases.sh counts each backslash escape on its own: a step name containing `\"`, one containing `\$` and one containing `\\` each count as replaced, exiting 0, when the REPLACES: name spells that escape removed (`"`, `$`, `\`) ⟦criterion 5⟧
- [ ] unreplaced-cases.sh unescapes only the step's name, never the REPLACES: name: for step name `a\\$b` the REPLACES: name `a\$b` counts as replaced, exiting 0, while a REPLACES: name keeping the step's escapes exactly still counts ⟦criterion 6⟧
