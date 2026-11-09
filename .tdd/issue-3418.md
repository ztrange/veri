# Plan for #3418 — dispatch.sh reads an issue with no comments as a silent exit instead of crashing on last_comment

- [ ] Dispatch handling an exited conductor whose issue has zero comments (the comments listing returns no items, faked at the gh process boundary in-process, never by stubbing last_comment) classifies it as a silent exit and exits 0, where it now raises IndexError and exits 2; pinned by one small unit case in skills/tdd/scripts/tests/py/unit/test_dispatch.py ⟦criterion 1⟧
