# Plan for #4050 — PRD 025.13: veri reads no bash .test.sh suites

- [x] every case that names a `.test.sh` suite while pinning quoting, escaping or bullet handling of a replaces-case step names a `.py` suite instead, its assertions unchanged ⟦criterion 4⟧
- [ ] `replaces_case.parse` returns `None` for a step whose suite ends in `.test.sh`, and `replaces_case.refusal` then says the suite "is not a .py file" ⟦criterion 1⟧
- [ ] `wrong-test-route.sh` treats a `.test.sh` file as no test file: a case defined only by a `name="<case>"` line in one is reported as missing, with the exit code any missing case gets ⟦criterion 2⟧
- [ ] `case_reader.cut_cases` over a file holding only a `name="…"` line returns no case; the fixture `run-finished.test.sh.txt` and the cases whose subject is the bash suite format are deleted ⟦criterion 3⟧ ⟦criterion 4⟧
