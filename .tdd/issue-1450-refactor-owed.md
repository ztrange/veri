### ledger-steps.sh reports a step whose prose quotes a criterion marker with only the criterion of its trailing marker run, and a step whose prose quotes a phases marker as a plain open step whose next-phase answer is exit 3 ⟦criterion 1⟧
- test-only | hoist the quoted prose "a step tagged ⟦criterion 2⟧ is refused twice", which both #1450 cases in test_ledger_steps.py repeat, into one module constant
- out-of-scope | KIND_RE.search(step) in ledger_steps still reads a kind marker from the prose; plan step 2 owns that change
- out-of-scope | multi_tag_refusal still counts criterion tags over the whole step text; plan step 5 owns that change
