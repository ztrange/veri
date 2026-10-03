# Plan for #706 — claude-md-guards-green loses its dead stubs and its misleading probe name

- [ ] In claude-md-guards-green.test.sh, the roster probe's function name and the first case's name say they check presence in `make test`'s roster, and neither contains the word "green" ⟦diff-checked⟧ ⟦criterion 1⟧
- [ ] The two planted-roster probes (the one naming each missing guard, the one on a roster naming no suite) write no guard stubs and hand the roster probe no stub directory ⟦diff-checked⟧ ⟦criterion 2⟧
- [ ] Record of a manual check: each planted-roster probe, with the roster probe broken on purpose, goes red naming the guard or the empty roster, then is put back ⟦human-owed⟧ ⟦criterion 2⟧
- [ ] The started-child case still runs the roster probe with its failing stubs standing in as HERE, so a probe that starts a guard by `$HERE/<guard>` touches a `.started` file ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] Record of a manual check: the started-child case goes red when the roster probe is made to start a guard, then is put back ⟦human-owed⟧ ⟦criterion 3⟧
- [ ] The started-child case and the header case keep their names and assertions unchanged by the branch ⟦diff-checked⟧ ⟦criterion 4⟧
- [ ] make test is green ⟦full-suite⟧ ⟦criterion 5⟧
