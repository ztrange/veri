# Plan for #390 — status.sh, metrics.sh and classify-bail.sh read a stopped run

- [x] status.sh renders a run whose log ends with a stop mark as `stopped <mode>`, and with STATUS_JSON/--json reports "state": "stopped" with the mode in a stop_mode key ⟦criterion 1⟧
- [ ] a resume mark after a stop mark makes status.sh render that run as running again ⟦criterion 2⟧
- [ ] metrics.sh prints an Outcome line naming the stop mode and the at boundary for a log whose ending mark is stop, and ends the issue wall at that stop mark ⟦criterion 3⟧
- [ ] a resume mark after a stop mark makes metrics.sh print the no-ending-mark Outcome for a run that has not ended since ⟦criterion 4⟧
- [ ] classify-bail.sh exits 2 for stopped, stop, at-ledger, at-leaf and now ⟦criterion 5⟧
- [ ] dashboard_endpoints.py run_ended answers false for a run whose log carries a stop mark and no done or bail ⟦criterion 6⟧
