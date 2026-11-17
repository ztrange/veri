# Plan for #4221 — PRD 035.3a1: a verifier's verdict line names the work tree it judged

- [x] under VERI_EVENT_STRICT=1 a `verdict` carrying `tree=<sha>` is written and one carrying a `tree` that is not a sha exits 2; JOURNAL.md's `verdict` row states `tree` ⟦criterion 2⟧
- [x] verify writes `tree=<the guard's before tree>` on every `verdict` line, and no `tree` key when the guard took no tree ⟦criterion 1⟧
