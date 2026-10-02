# Plan for #671 — a step marked ⟦replaces-case⟧ may delete exactly the bash case it names, so a port can replace an implementation case under ADR 0027

- [x] for a step whose step text carries `⟦replaces-case⟧`, the develop-green prompt `build-develop-prompt.sh green` builds permits deleting the one bash case the step names, and still forbids modifying or deleting any other case ⟦criterion 1⟧
- [x] for a step whose step text does not carry `⟦replaces-case⟧`, the develop-green prompt `build-develop-prompt.sh green` builds is byte-identical to the one it builds today ⟦criterion 2⟧
- [x] for a step whose step text carries `⟦replaces-case⟧`, the revise prompt `build-develop-prompt.sh revise green` builds permits deleting the one bash case the step names, and still forbids modifying or deleting any other case, while without the mark it is byte-identical to today's
- [x] for a `--step` carrying `⟦replaces-case⟧`, the verify-green prompt `build-verify-prompt.sh green` builds tells the verifier to PASS only when the named bash case is gone and a pytest case asserting the same behaviour was added, and to REJECT a deletion or modification of any other case ⟦criterion 3⟧
- [x] for a `--step` without `⟦replaces-case⟧`, or no `--step` at all, the verify-green prompt `build-verify-prompt.sh green` builds is byte-identical to the one it builds today ⟦criterion 4⟧
- [x] `build-verify-prompt.sh` takes the same arguments as today, and a green call with an extra positional argument beyond the target test id still exits 2 with nothing on stdout ⟦criterion 5⟧
- [x] `ledger-steps.sh` prints an open `⟦replaces-case⟧ ⟦criterion k⟧` step with kind `step`, added `0` and criterion `k`, and `next-unchecked.sh` prints it as the next step like any other ⟦criterion 6⟧
- [ ] `add-ledger-step.sh` does not count a `⟦replaces-case⟧` step against `VERI_STEP_GROWTH` unless that step is also marked `⟦added⟧` ⟦criterion 6⟧
- [ ] SKILL.md's *Scope & plan* section says a criterion replacing an implementation case under ADR 0027 is planned as one step marked `⟦replaces-case⟧` naming the suite path and the case's exact name, and that such a step's Red is the pytest case failing against the code before the change ⟦criterion 7⟧
- [ ] CONTEXT.md defines *contract case*, *implementation case* and the `⟦replaces-case⟧` mark ⟦criterion 8⟧
