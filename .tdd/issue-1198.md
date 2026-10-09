# Plan for #1198 — supervise.sh reads its timing tunables as bash arithmetic: octal windows, kills that never fire, endless retries, an orphaned leaf

- [x] A `VERI_HEARTBEAT` with leading zeros is read as decimal: `010` is a 10-second silence window, not an 8-second one, and `08` is an 8-second window that fires rather than an arithmetic error that never kills ⟦criterion 1⟧
- [x] A `VERI_TIMEOUT` with leading zeros is read as decimal: `010` is a 10-second hard cap, not 8, and `08` is an 8-second cap that fires rather than an arithmetic error that never kills ⟦criterion 1⟧
- [x] A settled `.tdd/issue-<n>-timeout` holding a value with leading zeros (`010`) is read as a decimal hard cap of 10 seconds, not 8 ⟦criterion 1⟧
- [ ] A `VERI_STUCK_RETRIES` with leading zeros is read as decimal: `08` allows exactly 8 retries after killed-stuck and then reports killed-stuck (exit 2), never retrying without end ⟦criterion 1⟧
- [ ] A `VERI_HEARTBEAT` that is not a non-negative decimal integer (`abc`, `1.5`, `-1`) is refused with exit 2 before the leaf is launched, stderr `supervise: VERI_HEARTBEAT is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧
- [ ] A `VERI_TIMEOUT` that is not a non-negative decimal integer (`abc`, `1.5`, `-1`) is refused with exit 2 before the leaf is launched, stderr `supervise: VERI_TIMEOUT is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧
- [ ] A settled `.tdd/issue-<n>-timeout` holding a value that is not a non-negative decimal integer (`abc`, `1.5`) is refused with exit 2 before the leaf is launched, stderr `supervise: <settled file path> is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧
- [ ] A `VERI_STUCK_RETRIES` that is not a non-negative decimal integer (`abc`, `1.5`, `-1`) is refused with exit 2 before the leaf is launched, stderr `supervise: VERI_STUCK_RETRIES is not a number: '<value>'`, leaving no leaf running ⟦criterion 1⟧
