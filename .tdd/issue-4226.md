# Plan for #4226 — PRD 035.4c1: a ledger rewrite records each reworded step

- [ ] under VERI_EVENT_STRICT=1 `step-reworded` with text keys `from` and `to` is accepted; JOURNAL.md states it ⟦criterion 1⟧
- [ ] `ledger-growth.sh record-rewrite <pre> <ledger>` writes one `step-reworded from=<old> to=<new>` per position whose step text differs when the step counts match ⟦criterion 2⟧
- [ ] when the step counts differ `record-rewrite` writes no `step-reworded` and exits as before ⟦criterion 2⟧
- [ ] `SCRIPTS.md`'s `ledger-growth.sh` entry states the event (SC270) ⟦criterion 3⟧
