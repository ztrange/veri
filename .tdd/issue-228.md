# Plan for #228 — A verifier leaf re-invoked after its turn ends appends a no-op result, and extract-result.sh reads that instead of the verdict

- [ ] A leaf log whose last result record has no VERDICT: line, but an earlier result record does, yields that verdict and its reason — exit 0 on PASS, 1 on REJECT — not exit 2
- [ ] A leaf log with no VERDICT: line in any result record still exits 2 with the same diagnostic
- [ ] The newest VERDICT: wins when more than one result record carries one
