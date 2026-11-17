# Plan for #4224 — PRD 035.4a: every leaf event names its leaf, and the metrics count per leaf kind

- [x] under VERI_EVENT_STRICT=1 `exit`, `retry`, `usage` and `verdict` each accept the optional text key `name`; JOURNAL.md states it on each ⟦criterion 1⟧
- [x] supervise writes on `exit` and `retry` the `name` its `launch` line carries ⟦criterion 1⟧
- [x] harvest-usage writes on `usage` the name of the leaf whose log it read ⟦criterion 1⟧
- [x] verify writes on `verdict` the name of the verifier leaf it launched ⟦criterion 1⟧
- [ ] `metrics.sh <n> --json` holds `leaves` keyed by leaf kind: a named line under its own kind, an unnamed one under its paired `launch`'s, one pairing with none under `unnamed` ⟦criterion 2⟧
- [ ] on a journal mixing named and unnamed lines, the `leaves` entries' attempts, wall seconds and cost sum to the `phases` entries' ⟦criterion 3⟧
- [ ] `PUBLISHED.md` states `leaves` (PB17) ⟦criterion 4⟧
