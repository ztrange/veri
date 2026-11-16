# Plan for #3988 — PRD 021.8: a dead supervisor's `leaf.owner` never blocks a launch

- [x] supervise.sh writes .tdd/leaf.owner with `<pid> <name>` on line 1 and its start time as `ps -o lstart=` prints it on line 2 ⟦criterion 1⟧
- [x] a launch reading a leaf.owner whose pid is alive under a different start time launches ⟦criterion 2⟧
- [x] a leaf.owner whose pid is alive under the same start time refuses the launch ⟦criterion 3⟧
- [ ] a leaf.owner with no line 2 whose pid is alive refuses the launch ⟦criterion 3⟧
- [ ] a leaf.owner with a line 2 whose live pid's start time ps cannot read refuses the launch
- [ ] the supervise.sh entry of SCRIPTS.md states the two-line leaf.owner and when it refuses, graded ⟦criterion 5⟧
