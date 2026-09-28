### `wait-ci.sh` takes the head sha it waits for as an argument, and while the PR's reported `headRefOid` is a different commit it exits 3 (pending) at the end of its slice even when that other commit's checks all completed SUCCESS ⟦criterion 1⟧
- the `across` and `total` cases in wait-ci.test.sh repeat the same persistent-dir setup (`mkdir -p "$work/<n>/.tdd"; : > <n>.clock; : > <n>.json.calls`), which a small helper could replace — code from before this cycle, so not applied here
### SKILL.md's Draft PR step passes the sha it just pushed (`git rev-parse HEAD`) to every `wait-ci.sh` call ⟦criterion 2⟧
- cases 28 and 29 of skill-draft-pr.test.sh both check `line_of "$wait_ci_run"` and add a near-identical "runs no $S/wait-ci.sh, so … could not be checked" problem; that could be one helper
