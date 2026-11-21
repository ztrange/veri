# Plan for #4576 — bail events missing from the run journal (veri-dashboard #13, #19, #28), so status and metrics see no bail

- [ ] `event.sh bail` run with `VERI_ISSUE` empty and `VERI_STATE_LABEL_ISSUE=<n>` (the conductor's export) writes the bail, carrying issue `<n>`, to `<n>`'s journal ⟦criterion 1⟧
- [ ] the journal's `<n>.metrics.json` `run.bails` lists both bails of a journal holding two ⟦criterion 2⟧
