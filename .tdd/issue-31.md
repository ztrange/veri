# Plan for #31 — an "already satisfied" step outcome: verify-pin

- [x] build-verify-prompt.sh pin assembles a blind verifier prompt from the spec and test path alone, carrying the pin checks (passes now; fails under a behaviour-removing mutation; behaviour-level)
- [x] verify.sh pin exits 0 on PASS, 1 on REJECT, 2 on no verdict, like the other phases
