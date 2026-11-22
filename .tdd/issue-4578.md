# Plan for #4578 — The test-quality pass cannot report a fixed sleep or quiet-window wait

- [x] `test-quality.sh record <n>` records a `FINDING: fixed-wait | <file>::<case> | <why>` line whose file defines the case, exit 0 ⟦criterion 1⟧
- [ ] `develop-test-quality.md` names the `fixed-wait` kind and what it is, in its kind list and its `FINDING:` report line, graded by TQP2 ⟦criterion 2⟧
- [ ] `DRAFT-PR.md` gives a `fixed-wait` finding no step and lists it `not fixed` with why `fixed-wait`, and `SCRIPTS.md`'s `test-quality.sh` entry names the four kinds `record` accepts, graded by DP191, DP193 and SC621 ⟦criterion 3⟧
