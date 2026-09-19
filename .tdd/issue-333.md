# Plan for #333 — skill-leaf-env.test.sh runs its 10 independent leaf launches one after another instead of concurrently

- [x] skill-leaf-env.test.sh's 10 launches (case 1's 5 developer lines and case 2's 5 verifier lines) all overlap: a start and a finish marker each launch writes show every launch's start marker preceding every launch's finish marker ⟦criterion 1⟧
- [x] with launches concurrent, a launch whose leaf does not see VERI_TEST_CMD is still reported by skill-leaf-env.test.sh against the launch line it came from, by line number ⟦criterion 2⟧
- [x] case 3 of skill-leaf-env.test.sh still reads all 10 launch trees' event logs only after every launch has completed, with its assertions unchanged ⟦criterion 3⟧
- [ ] one launch line's sentinel deliberately broken is reported naming that one line, while the other 9 launches still pass ⟦criterion 4⟧
- [ ] skill-leaf-env.test.sh's count line and every existing problem/report message format are unchanged, and make test is green ⟦criterion 5⟧
