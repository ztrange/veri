# Plan for #172 — A verifier can change the tree through Bash, and nothing checks before the conductor commits it

- [x] verify.sh exits 2 when the verifier leaf leaves any tracked or untracked non-ignored file changed or moves HEAD, with the changed paths on stdout
- [x] After that exit 2 the tree and HEAD are restored to exactly what they were before the verifier launched, uncommitted developer work included
- [x] A verifier that mutates a file and restores it before ending gets its verdict's normal exit code
- [ ] The tree-integrity check holds when VERIFY_LEAF_ARGS overrides the leaf's flags
