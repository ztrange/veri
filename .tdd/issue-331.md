# Plan for #331 — metrics.test.sh and harvest-usage.test.sh start far more python3 processes than they have assertions

- [x] harvest-usage.test.sh cases 1 and 2 launch the fixture leaf through a real run-leaf.sh against a stub claude, with its combined output in .tdd/<leaf>.log, not through supervise.sh and never a hand-written log, and that log's usage record is still not its last line ⟦criterion 4⟧
- [x] harvest-usage.test.sh case 2 still asserts no usage line and a stderr diagnostic naming the harvester and the leaf, and its setup probe still refuses to run when the event log a real writer left behind is empty ⟦criterion 5⟧
- [x] harvest-usage.test.sh case 1's eight-number comparison runs in one python3 process and still goes red naming the one field whose expected value is wrong ⟦criterion 3⟧
- [ ] harvest-usage.test.sh's total python3 starts, counted by a PATH-first counting shim, are at most 8 ⟦criterion 2⟧
- [ ] metrics.test.sh's total python3 starts, counted by a PATH-first counting shim, are at most 21 — one per case — with every case's assertions unchanged ⟦criterion 1⟧
- [ ] harvest-usage.test.sh case 3 is unchanged: a hand-written one-line log fixture, no launch, exit 2, no usage line, a diagnostic naming the harvester or leaf-role ⟦criterion 6⟧
- [ ] every metrics.test.sh and harvest-usage.test.sh assertion that passed before still passes, and make test is green ⟦criterion 7⟧
