# Plan for #4719 — go-red probe cannot resolve a node or Python test title: defining_file scans only *_test.go

- [x] `defining_file()` resolves a `node --test` case title written as `test("<title>", …)` in a `*.test.mjs` file to that file ⟦criterion 1⟧
- [x] `defining_file()` resolves a pytest case name to the one `test_*.py` file defining `def <name>` ⟦criterion 2⟧
- [x] `classify-bail.sh go-red-probe-unresolvable` names a category, and `event.sh` accepts a `bail` event with that cause ⟦criterion 3⟧
- [x] `skills/tdd/BAIL.md` lists `go-red-probe-unresolvable` among the bail causes: a `go-red-step.sh` probe stop (exit 2) on a case no test file defines ⟦skill-edit⟧
