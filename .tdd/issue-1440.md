# Plan for #1440 — Nothing pins that supervise ignores VERI_NO_VERDICT_RETRIES since #1264's port

- [ ] A supervised leaf that never answers is launched the same number of times with VERI_NO_VERDICT_RETRIES set to a value larger than VERI_STUCK_RETRIES as without it — the supervisor's retry count comes from VERI_STUCK_RETRIES alone — pinned by a case in tests/py/test_supervise.py that goes red when supervise.py reads VERI_NO_VERDICT_RETRIES as its retry count; no production change expected ⟦criterion 1⟧
