# Plan for #4053 — PRD 025.18: one prose table of every tunable

- [ ] veri/README.md's `## tunables` section holds a table with one row per key of tunables.TUNABLES — name, default, refusal or "its readers' own words" — and a unit case fails naming a key with no row or a row naming no key ⟦criterion 1⟧
- [ ] the unit case also fails naming the name when a row's default differs from tunables.default(name) ⟦criterion 2⟧
