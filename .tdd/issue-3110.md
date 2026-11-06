# Plan for #3110 — The deleted-case guard recognises a JS case however Jest/Mocha spell it

- [x] deleted_cases reports a single-quoted it('…') case deleted from a .test.js file (case in skills/tdd/scripts/tests/py/test_verify.py) ⟦criterion 1⟧
- [x] deleted_cases reports a backtick it(`…`) case deleted from a .test.js file (case in skills/tdd/scripts/tests/py/test_verify.py) ⟦criterion 1⟧
- [x] deleted_cases reports a double-quoted test("…") case deleted from a .test.js file (case in skills/tdd/scripts/tests/py/test_verify.py) ⟦criterion 1⟧
- [ ] deleted_cases reports a single-quoted test('…') case deleted from a .test.js file (case in skills/tdd/scripts/tests/py/test_verify.py) ⟦criterion 1⟧
- [ ] deleted_cases reports an it("…") case deleted from a .spec.js file (case in skills/tdd/scripts/tests/py/test_verify.py) ⟦criterion 1⟧
- [ ] deleted_cases does not report a test('…') case kept in a .spec.js file while another case of that file changes (case in skills/tdd/scripts/tests/py/test_verify.py) ⟦criterion 1⟧
- [ ] deleted_cases does not report a test('…') case renamed in a .spec.js file with its body unchanged (case in skills/tdd/scripts/tests/py/test_verify.py) ⟦criterion 1⟧
- [ ] verify.py holds no JS case pattern or JS test-file suffix of its own: the deleted-case guard takes both from the module that already defines them (case_reader.is_js_test_file and js_tests.CALL), with no second copy in verify.py, and the fast tier and test_verify.py stay green ⟦diff-checked⟧
- [ ] Go-red control: with verify.py pointed back at its own private JS pattern (one it("…"), .test.js only), criterion 1's cases go red; restored, green ⟦human-owed⟧ ⟦criterion 2⟧
