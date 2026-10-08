# Plan for #1155 — detach-command.sh wait busy-loops with no pause when VERI_POLL is not a non-negative number

Plan's choices: a bad VERI_POLL is refused once, loudly (exit 2 before any round, one stderr line naming VERI_POLL and the value) rather than falling back to 1; and the values `sleep` accepted on main (`1e-1`, `0.1s`, `1m`) get that same single refusal rather than being parsed as `sleep` would, following the `VERI_KILL_POLL` precedent in supervise.sh.

- [ ] Through the entry point, `detach-command.sh wait <name>` with VERI_POLL set to `abc` or `-1` exits 2 before any polling round, writing exactly one stderr line that names VERI_POLL and the value and nothing on stdout, and never pauses or loops; the pytest case pinning the per-round busy poll for those values is retired with it ⟦criterion 1⟧
- [ ] Through the entry point, `detach-command.sh wait <name>` with VERI_POLL set to a value `sleep` accepted on main but that is not a plain non-negative decimal (`1e-1`, `0.1s`, `1m`) gets the same single refusal: exit 2 before any round, one stderr line naming VERI_POLL and the value ⟦criterion 1⟧
- [ ] `detach-command.sh wait <name>` with VERI_POLL unset or empty still pauses 1 second between rounds, and with `0` or `0.05` pauses exactly that long, with nothing on stderr ⟦criterion 1⟧
- [ ] The new handling has been watched go red: the per-round busy poll put back on purpose, the case seen failing, the fix restored ⟦human-owed⟧ ⟦criterion 2⟧
