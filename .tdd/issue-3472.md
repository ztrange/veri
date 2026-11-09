# Plan for #3472 — A missing-reroute's unpinnable case bails as no-verdict (system) instead of a process failure naming unpinnable-missing

- [x] `classify-bail.sh unpinnable-missing` prints `process` and exits 0 (a small in-process case in the classify_bail unit suite) ⟦criterion 1⟧
- [ ] `pin-reject-route.sh --missing-reroute` on a reason saying `stays green` prints `unpinnable-missing` on stdout, still exits 2, writes exactly one `unpinnable-missing` event and leaves the ledger untouched ⟦criterion 2⟧
- [ ] `pin-reject-route.sh --missing-reroute` with fewer than four further arguments still exits 2 printing nothing on stdout and a usage line on stderr ⟦criterion 2⟧
- [ ] ⟦skill-edit⟧ `skills/tdd/BAIL.md`: the cause list gains an `unpinnable-missing` bullet — a missing-reroute's demanded case is green on the before-state and cannot be pinned; a **process** failure ⟦criterion 3⟧
- [ ] ⟦skill-edit⟧ `skills/tdd/PIN.md`: the REJECT branch bails with cause `unpinnable-missing`, a process failure, when `pin-reject-route.sh --missing-reroute` exits 2 printing `unpinnable-missing`, and keeps the system bail only for a bare exit 2 (no longer saying the stays-green case prints neither) ⟦criterion 3⟧
- [ ] ⟦skill-edit⟧ `skills/tdd/SCRIPTS.md`: the `pin-reject-route.sh` entry (and its SC87 row) says that under `--missing-reroute` a reason saying `stays green` prints `unpinnable-missing` on stdout with its exit 2 and its one event, while bad arguments still print nothing on stdout
