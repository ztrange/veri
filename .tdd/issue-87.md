# Plan for #87 — Make the shell suites hermetic against ambient VERI_* tunables

- [x] supervise-retry.test.sh reports 1 passed, 0 failed with VERI_STUCK_RETRIES=0 in the caller's environment, exactly as with the variable unset
- [ ] supervise.test.sh's hung-leaf case runs the leaf exactly once under an ambient VERI_STUCK_RETRIES=3 — one killed-stuck line, no retry
- [ ] verify.test.sh's hung verifier leaf case runs the leaf exactly once under an ambient VERI_STUCK_RETRIES=3, so its verdict and wall time do not depend on the caller's environment
