# Plan for #401 — affected-suites.sh places no file under scripts/prompts/, so any diff touching a prompt falls through to the fail-closed branch and runs every suite

- [x] a range whose only changed file is a prompt under scripts/prompts/ answers with the suites that name that prompt, not with every suite ⟦criterion 1⟧
- [x] a range touching both a prompt and a suite answers with that suite and the prompt's suites, and does not widen to every suite ⟦criterion 2⟧
- [x] a file that matches no placement rule still widens the answer to every suite ⟦criterion 3⟧
- [x] a widened answer names on stderr the file that forced the widening ⟦criterion 4⟧ ⟂ refactor pending
