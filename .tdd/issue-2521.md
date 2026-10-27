# Plan for #2521 — stop-reason.sh names the check a refused run stopped on

- [ ] For a run whose end mark is a `preflight-refused` event, `stop-reason.sh <n>` exits 0 and prints `refused <check>`, naming the `check` recorded in that refusal event, both when the run has a conductor log and when it has none, pinned by a case in `skills/tdd/scripts/tests/py/unit/test_stop_reason.py` ⟦criterion 1⟧
- [ ] `done`, `bailed`, `stopped`, `killed-external` and the generic causes print exactly as now, pinned by the existing cases staying green ⟦full-suite⟧ ⟦criterion 2⟧
