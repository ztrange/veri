# Plan for #2328 — Two first-ever claims in one lane: the loser's label create fails 'already exists' and leaves its issue with neither label

- [ ] When the taken:<lane> lookup answers 404 and gh label create fails with "already exists", the claim (unlabel-issue.sh) adds taken:<lane> to the issue and exits 0 — a small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py faking gh at the github.py boundary ⟦criterion 1⟧
- [ ] When the taken:<lane> lookup answers 404 and gh label create fails with anything other than "already exists", the claim still exits 2 and adds no label to the issue — a small in-process case in skills/tdd/scripts/tests/py/unit/test_unlabel_issue.py faking gh at the github.py boundary ⟦criterion 1⟧
