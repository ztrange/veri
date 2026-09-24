# Plan for #457 — skill-leaf-env.test.sh case 2 is a race: launch_over can break the wait before the completion file exists

- [x] A detached launch whose leaf answers and whose completion file lands only after every recorded pid has exited is reported by what the leaf saw, never as `<no completion file under leaf …>` ⟦criterion 1⟧
- [x] A launch whose derived leaf name no completion file is written under is still reported as a naming fault, answered well inside the wait budget rather than after it ⟦criterion 2⟧
- [x] A launch line that reaches no supervisor at all is reported as `<no leaf ran>` by a case of its own ⟦criterion 3⟧
- [ ] Removing any one of the three behaviours — trusting the leaf's answer after a late completion file, the fast naming-fault report, the `<no leaf ran>` report — turns a named case of skill-leaf-env.test.sh red ⟦criterion 4⟧
