# Plan for #4735 — A red revise re-checked as a pin compares stale red reason files, so same-reject skips pin-reject-route

- [x] After a red revise attempt k whose re-check ran verify-pin and REJECTed, attempt k+1's `same-reject.sh` compares `.tdd/verify-red-<k>.reason` with a reason file holding the pin verifier's reason (`.tdd/verify-pin.reason`'s text), not the stale red one, so a pin reason different from the prior red reason is not judged a same reject and attempt k+1 is launched ⟦criterion 1⟧
- [ ] After a red revise attempt k whose re-check ran verify-pin and REJECTed, `revise.sh` runs `pin-reject-route.sh .tdd/verify-pin.reason .tdd/issue-<n>.md <step> <target-test>` (the step's `TARGET_TEST` from `.tdd/develop-red.out`) before attempt k+1, and on its exit 1 goes on to attempt k+1 ⟦criterion 1⟧
- [ ] On `pin-reject-route.sh` exit 0 (the step retired) after a red revise's verify-pin REJECT, `revise.sh` launches no attempt k+1 and exits 1 with a last line naming the retirement
- [ ] On `pin-reject-route.sh` exit 2 after a red revise's verify-pin REJECT, `revise.sh` launches no attempt k+1 and exits 2
