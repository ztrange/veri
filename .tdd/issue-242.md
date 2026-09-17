# Plan for #242 — push-branch.test.sh waits 14 s of real backoff on every make test since #232

- [x] push-branch.test.sh completes in under 5 s of wall time on an unreachable origin: every case that pushes to a missing origin sets VERI_PUSH_BACKOFF=0
- [x] hermetic-suites.test.sh fails when a suite invokes push-branch.sh without VERI_PUSH_BACKOFF in its environment, naming the suite and line ⟂ refactor pending
