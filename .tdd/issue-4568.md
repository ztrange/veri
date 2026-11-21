# Plan for #4568 — The verifier REJECT rate doubled on 2026-10-26 (7.8% to 17.6% per verify) with revise cycles flat

- [ ] `reject-breakdown.sh`, fed `<YYYY-MM-DD> <report>` lines on stdin, prints one `week <monday>: REJECT per verify <pct> (<rejects> of <verifies>)` line per week, summing the PASS and REJECT columns of each report's `#### By phase` table ⟦criterion 1⟧
- [ ] under each week line, `reject-breakdown.sh` prints one `  phase <phase>: <rejects> of <verifies>` line per verifier phase with a verdict that week ⟦criterion 1⟧
- [ ] under each week, `reject-breakdown.sh` prints one `  reason <phase> <class>: <rejects>` line per reason class: green REJECTs per check from the `Green rejects by check:` line, the rest of each phase's REJECTs as `unclassified` ⟦criterion 1⟧
- [ ] `reject-breakdown.sh` exits 2 naming the line for a stdin line that is not `<YYYY-MM-DD> <path>` or a report it cannot read, and exits 3 when stdin names no report
- [ ] the breakdown run over the main clone's reports, its diagnosis posted on #4568: the phase and reason class carrying the 2026-10-26 increase and the change that explains it ⟦criterion 2⟧
- [ ] each REJECT class the diagnosis names is judged real or spurious, a spurious one fixed or filed as a follow-up ⟦criterion 3⟧
