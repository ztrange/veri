# Plan for #956 — verdict-* supervisions write leaf-role and harvest-usage diagnostics to stderr for a path that is meant to be silent

- [x] `supervise.sh verdict-<phase> <cmd>` writes no `leaf-role:` line to stderr, while its exit code and its completion file `.tdd/verdict-<phase>.exit` are unchanged and it still appends no `launch` or `exit` event to `.tdd/events.jsonl` ⟦criterion 1⟧
- [x] `supervise.sh verdict-<phase> <cmd>` whose log holds no closing result record writes no `harvest-usage.sh:` line to stderr ⟦criterion 1⟧
- [x] `supervise.sh` given a name that is neither a known role nor `verdict-*` (e.g. `bogus-x`) still writes the `leaf-role: … unknown leading word` diagnostic to stderr ⟦criterion 2⟧
- [ ] a `develop-*` or `verify-*` supervision whose log holds no closing result record still writes the `harvest-usage.sh: no closing result record` line to stderr ⟦criterion 3⟧
