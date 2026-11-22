# Plan for #4642 — tests-frozen.sh has no verb to re-record named stale cases on a human's word after a rerecord-refactored skip

- [x] `tests-frozen.sh rerecord-approved <ledger> --approval <text> <case>...` re-records exactly the named case at its HEAD body with its `helpers:` line, every other record byte-identical, and `check-earlier` still refuses the unnamed stale case ⟦criterion 1⟧
- [x] `rerecord-approved` naming a case `rerecord-refactored` skipped (helper lines moved) exits 0 and `check-earlier` then passes ⟦criterion 2⟧
- [x] `rerecord-approved` naming a case no record holds exits 2 naming it and writes nothing, and with no case named exits 2 ⟦criterion 3⟧
- [x] `rerecord-approved` naming a recorded case absent at HEAD exits 2 naming it and writes nothing ⟦criterion 4⟧
- [ ] `rerecord-approved` whose record cannot be written exits 2 and restores every record it had rewritten byte-identical ⟦criterion 5⟧
- [ ] `rerecord-approved` logs one `tests-frozen-rerecord-approved` event per re-recorded case with `case`, `file` and `approval`, accepted under `VERI_EVENT_STRICT=1`, and without the approval text exits 2 writing no event ⟦criterion 6⟧
- [ ] the usage text `tests-frozen.sh` prints names `rerecord-approved`, and `skills/tdd/SCRIPTS.md`'s `tests-frozen.sh` entry and the shim's usage block name its arguments, exits and event ⟦criterion 7⟧
- [ ] `skills/vbail/SKILL.md` *Classify first* routes a `needs-user` verify-refactor bail answered re-record to `tests-frozen.sh rerecord-approved`, graded against a new B row ⟦criterion 8⟧
- [ ] helper collection follows calls transitively within the case's file, so `rerecord-refactored` re-records a Go case whose direct helper call moved into a new helper that calls it ⟦criterion 9⟧
- [ ] the transitive helper walk terminates on a self-recursive helper and on a mutually recursive pair, each helper's lines counted once ⟦criterion 9⟧
- [ ] a record whose `helpers:` digest was computed by the non-transitive collection still passes `check` and `check-earlier` after the change, naming no case weakened or edited, while a digest matching neither collection still exits 1 ⟦criterion 10⟧
