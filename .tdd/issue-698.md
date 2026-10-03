# Plan for #698 — Three suites whose cases cannot go red on what they guard are made to fail on it

- [x] skill-suite-runs.test.sh case 1 passes on a SKILL.md whose Green section and Refactor loop name no full-suite run at all (the "Neither … runs the full suite" sentences of the Green and Refactor sections deleted) ⟦criterion 1⟧
- [x] skill-suite-runs.test.sh goes red on a SKILL.md whose Green section says develop-green keeps the full suite green ⟦criterion 1⟧
- [ ] prompt-test-tiers.test.sh, judged on the diff: `build-develop-prompt.sh revise red` is built and checked inside the "develop-revise redoing red …" case, so its non-zero exit is charged to that case by name, and the develop-red/refactor/reconcile case no longer builds it ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] add-ledger-step.test.sh: the stub lib/ledger.sh case goes red, naming the stderr printed, whenever the stubbed add-ledger-step.sh run prints anything on stderr, and the stubbed run prints nothing on stderr ⟦criterion 3⟧
- [ ] every other case in skill-suite-runs.test.sh, prompt-test-tiers.test.sh and add-ledger-step.test.sh is left unmodified by the branch ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 5⟧
