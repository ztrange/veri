# Plan for #1469 — pytest-leg.test.sh spends ~24 s of make test on repeated nested make runs and a real sleep

- [ ] No case in pytest-leg.test.sh waits on a real clock: the per-case timeout case runs under an injected VERI_PYTEST_TIMEOUT small enough that its over-time case does not sleep, and still shows that case failing, named as a timeout, while the leg reports the other case passed ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] Cases in pytest-leg.test.sh that assert on the same target's output under the same planted tree share one run of that target instead of each starting its own make, every assertion the suite made before still holds, and each still goes red against a broken Makefile pytest leg ⟦diff-checked⟧ ⟦criterion 2⟧
