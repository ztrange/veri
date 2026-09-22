# Plan for #418 — A leaf that runs a suite directly bypasses the count-line guard, so a partially-dead suite reads as green

- [x] Running one suite directly through the repository's suite runner exits non-zero, naming the suite, when that suite exits 0 without printing its `<n> passed, <m> failed` count line ⟦criterion 1⟧
- [x] That runner runs one named suite without setting `TESTS=`, so no nested make inherits it ⟦criterion 4⟧
- [x] The `make test` target and the direct invocation report a countless suite identically, from one guard rather than two that can drift
- [x] Every developer prompt names the one invocation to use for running a single suite ⟦criterion 2⟧
- [x] Every developer prompt that names `run-suite.sh` tells its leaf what to run when the target repository has no such runner ⟦added⟧ ⟦criterion 2⟧
- [x] Every blind verifier prompt names that same invocation, so a verifier cannot render PASS over a partially-dead suite ⟦criterion 3⟧
- [x] Every blind verifier prompt that names `run-suite.sh` tells its leaf what to run when the target repository has no such runner ⟦added⟧ ⟦criterion 3⟧
- [x] A suite pins the guard against the deliberately partially-dead fixture invoked directly, not only through the make target ⟦criterion 5⟧
