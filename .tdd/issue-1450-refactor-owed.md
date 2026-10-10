### ledger-steps.sh reports a step whose prose quotes a criterion marker with only the criterion of its trailing marker run, and a step whose prose quotes a phases marker as a plain open step whose next-phase answer is exit 3 ⟦criterion 1⟧
- test-only | hoist the quoted prose "a step tagged ⟦criterion 2⟧ is refused twice", which both #1450 cases in test_ledger_steps.py repeat, into one module constant
- out-of-scope | KIND_RE.search(step) in ledger_steps still reads a kind marker from the prose; plan step 2 owns that change
- out-of-scope | multi_tag_refusal still counts criterion tags over the whole step text; plan step 5 owns that change
### criterion-finished.sh accepts a ledger whose step prose quotes a criterion marker, with no more-than-one-criterion-tag refusal, and counts that step only toward the criterion of its trailing marker run ⟦criterion 2⟧
- test-only | the new test in test_criterion_finished.py and the multi-tag test just above it share the same loop: fake stdin, call `criterion_finished.main([k])` for k in "1"/"2", collect the answers into a dict. That loop could become one helper.
