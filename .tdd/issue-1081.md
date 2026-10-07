# Plan for #1081 — build-verify-prompt.test.sh's 'no verifier prompt carries the prediction' passes on an empty prompt

- [ ] The "no verifier prompt carries the prediction" case in build-verify-prompt.test.sh builds each phase (red, green, refactor, pin) with VERI_PREDICTED_FAILURE set and only that phase's normal arguments, and asserts for each phase that the builder exits 0, prints a non-empty prompt, and that the prompt carries neither the prediction text nor a request for a prediction ⟦criterion 1⟧
- [ ] Planting $VERI_PREDICTED_FAILURE into a verify template turns the "no verifier prompt carries the prediction" case red, watched to happen, then the template restored ⟦human-owed⟧ ⟦criterion 1⟧
- [ ] A separate case in build-verify-prompt.test.sh pins that build-verify-prompt.sh refuses a fifth positional argument: exit 2 and nothing on stdout ⟦criterion 2⟧
