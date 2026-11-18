# Plan for #4337 — Preflight skips the baseline when CI is green on the commit or a local record matches its tree

- [x] A fresh launch whose base commit has a `CI` run concluded `success` on that exact sha starts neither the fast-tier nor the full-tier baseline run and goes on as on a green baseline ⟦criterion 1⟧
- [x] A `CI` answer that is red, pending, absent, unreadable (a `gh` failure or unparseable output) or about a sha other than the one under test runs the baseline ⟦criterion 6⟧
- [ ] `baseline-full-tier.sh --green` prints `skip` for a tree, fast and full command, skill commit pin and venv lock hash that `--record-green` recorded, and `run` for none recorded
- [ ] A record whose tree, fast or full command, skill commit pin or venv lock hash differs from the current ones answers `run` ⟦criterion 3⟧
- [ ] A corrupt or absent record answers `run` ⟦criterion 5⟧
- [ ] A recorded entry that is not green answers `run` ⟦criterion 4⟧
- [ ] A preflight whose baseline ran green records it with `--record-green`, and one whose baseline ran red records nothing ⟦criterion 4⟧
- [ ] A resume whose recorded green matches skips the baseline run and goes on ⟦criterion 2⟧
- [ ] ⟦skill-edit⟧ `skills/tdd/PREFLIGHT.md`: step 3 states the two sources, the fail-closed rule and the accepted trade-off (PF70, PF71); `CLAUDE.md`, `RESUME.md` and `SCRIPTS.md` follow ⟦criterion 8⟧
