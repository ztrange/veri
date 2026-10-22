# Plan for #1989 — supervise.py exempts a step from the verify-red-PASS gate when it names ⟦ci-repair⟧ anywhere, not only as a trailing marker

- [x] supervise refuses develop-green with exit 2 and its existing "has no verify-red PASS after its latest red leaf" message for a step that names ⟦ci-repair⟧ mid-sentence but not among its trailing markers, when the step's latest red leaf has no verify-red PASS (ci_repair_step reads the step's trailing markers the way tests_frozen.py does) ⟦criterion 1⟧
- [x] supervise still launches develop-green without a verify-red PASS for a step whose trailing markers include ⟦ci-repair⟧ ⟦criterion 2⟧
- [x] build_develop_prompt.py adds no fixture-repair fragment for a step naming ⟦fixture-repair⟧ mid-sentence but not among its trailing markers ⟦criterion 3⟧
- [ ] build_develop_prompt.py still adds the fixture-repair fragment for a step whose trailing markers include ⟦fixture-repair⟧ ⟦criterion 3⟧
