# Plan for #2304 — No case pins that grade-prose launches the grader once on a well-formed FAIL, so a relaunch could turn a FAIL into a PASS

- [ ] With VERI_NO_VERDICT_RETRIES=3, a grader stub returning a well-formed GRADES block that grades one requirement FAIL is launched exactly once, and grade-prose.sh exits 1 naming that requirement; pinned by a small in-process case in tests/py/unit/test_grade_prose.py (no production change expected; the case must go red if keeps_protocol rejects a FAIL) ⟦criterion 1⟧
