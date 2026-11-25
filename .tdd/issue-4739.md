# Plan for #4739 — A verify-pin REJECT retired because the hand mutation stays green removes the step's Red test changes

- [x] an unpinnable retire on a hand-mutation reason with no before-state-green clause deletes an untracked test file and restores a modified tracked test file to HEAD ⟦criterion 1⟧
- [x] an unpinnable retire on a "the real before-state stays green" reason leaves every test file as it was ⟦criterion 2⟧
- [ ] an unpinnable retire on a reason with both the before-state-green and the guard-mutation clause leaves every test file as it was ⟦criterion 3⟧
- [ ] a removing retire leaves the ledger rewrite, a .tdd/ file and a modified production file unchanged ⟦criterion 4⟧
- [ ] a hand-mutation reason whose target case fails prints revise, exits 1 and removes no test file ⟦criterion 5⟧
- [ ] a --missing-reroute retire through --already-holds removes no test file ⟦criterion 6⟧
- [ ] a removing retire deletes a test file staged as new but absent from HEAD and leaves it out of the index
- [ ] PIN.md's REJECT branch states which retires remove the Red test changes and how stays-green reasons route ⟦criterion 9⟧
- [ ] SCRIPTS.md's tick-ledger.sh --unpinnable and pin-reject-route.sh entries state the removal ⟦criterion 10⟧
