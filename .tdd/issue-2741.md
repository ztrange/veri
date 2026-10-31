# Plan for #2741 — A full test leg cut short by an xdist error still names the cases that failed

- [x] A pytest leg (`veri/pytest_leg.py`) whose run ends in an xdist INTERNALERROR after some cases had failed prints each failed case's node id ⟦criterion 1⟧ ⟂ refactor pending
- [ ] A pytest leg whose run ends in an xdist INTERNALERROR says on stderr that the leg was cut short ⟦criterion 1⟧
- [ ] A pytest leg whose run ends in an xdist INTERNALERROR after some cases had failed exits non-zero ⟦criterion 1⟧
