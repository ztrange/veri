# Plan for #949 — make test is red when the caller sets BASH_ENV: every suite's bash children re-source it and lose the PATH the suite built

- [x] A suite run by `make test` or by `make unit` sees neither `BASH_ENV` nor `ENV` in its environment, even when the caller exported both, pinned in `make-test-env.test.sh` ⟦criterion 1⟧ ⟂ refactor pending
- [ ] A suite run by `make test` that sets `BASH_ENV` itself for one case still has it in that case: a bash child it starts with its own `BASH_ENV` sources that file ⟦criterion 3⟧
- [ ] With `BASH_ENV` pointing at a file that prepends a directory to PATH, `pytest-leg.test.sh` and its unit-guard case give the same result under the recipe as with it unset, watched going red with the recipe change reverted and green with it restored ⟦human-owed⟧ ⟦criterion 2⟧
