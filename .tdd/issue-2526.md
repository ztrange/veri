# Plan for #2526 — metrics.sh says what a total covers when a run's conductor sessions are partly priced

- [x] For a run whose conductor log has a priced session and an unpriced one, metrics.sh's sentence about the total row says the total includes the priced sessions' conductor spend and leaves out the unpriced ones, agreeing with the total row, which counts the priced session's spend; pinned by a small pytest case in tests/py/test_metrics.py driving veri/metrics in-process ⟦criterion 1⟧
- [ ] All-priced, all-unpriced and usage-event runs report exactly as now, pinned by the existing cases staying green ⟦full-suite⟧ ⟦criterion 2⟧
