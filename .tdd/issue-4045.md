# Plan for #4045 — PRD 025.5: veri/ no longer holds the two modules only tests import

- [x] fast_tier_guard.py and event_roster.py live in tests/py, the suites that use them import them flat from there, no file names either as veri.<module>, veri/README.md's index lists neither and tests/py/README.md names both at their new path ⟦criterion 1⟧
- [x] fast_tier_guard.py has no if __name__ == "__main__" block ⟦criterion 2⟧
