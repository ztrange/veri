# Plan for #1957 — wrong-test-route.sh recognises Vitest/JS/TS test cases, quoted and ellipsis-cut names

Every case is a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py, driving wrong_test_route.main through run_cli against a throwaway repo under tmp_path (no process, no git).

- [x] A WRONG_TEST: or SUPERSEDED: line indented by one, two or three spaces is read as prose, not a route line: the existing #1865 case that treats a two-space-indented SUPERSEDED: line as real is changed to expect revise, for one, two and three spaces ⟦criterion 8⟧
- [x] A WRONG_TEST: line indented by one, two or three spaces naming an existing sibling case answers revise, not red ⟦criterion 8⟧
- [x] A WRONG_TEST: naming in backticks the exact title of an it('…') call in a foo.test.ts file routes red <title> ⟦criterion 1⟧
- [x] A WRONG_TEST: naming the title of an it(…) call routes red when the file is a *.test.* or *.spec.* file over each of .js .jsx .ts .tsx .mjs .cjs ⟦criterion 1⟧
- [x] A WRONG_TEST: naming the title of an it(…) call routes red when the call sits in a .js or .ts file under a __tests__/ directory whose name carries no .test or .spec ⟦criterion 1⟧
- [x] A .d.ts file is never a test file: a WRONG_TEST: naming the title of an it(…) call found only in foo.test.d.ts or __tests__/types.d.ts answers revise ⟦criterion 1⟧
- [x] A WRONG_TEST: naming the title of an it(…) call found only in a non-test source file (config.ts, src/testing/config.js) answers revise ⟦criterion 1⟧
- [x] A WRONG_TEST: naming the exact title of a test(…) call in a JS/TS test file routes red <title> ⟦criterion 2⟧ ⟂ refactor pending
- [ ] The .only and .skip forms of it(…) and test(…) (it.only, it.skip, test.only, test.skip) are cases: a WRONG_TEST: naming their title routes red <title> ⟦criterion 2⟧
- [ ] The call after an .each([...]) head and after an .each`…` tagged-template head (it.each, test.each) is a case: a WRONG_TEST: naming its title routes red <title> ⟦criterion 2⟧
- [ ] An it(…) or test(…) call commented out with // is not a case: a WRONG_TEST: naming only its title answers revise ⟦criterion 2⟧
- [ ] An it(…) or test(…) call inside a /* … */ block comment is not a case: a WRONG_TEST: naming only its title answers revise ⟦criterion 2⟧
- [ ] A case name in double quotes on the WRONG_TEST: line is a candidate: it routes red <title> to the JS/TS case of that exact title ⟦criterion 3⟧
- [ ] A case name in curly quotes (“…”) on the WRONG_TEST: line is a candidate: it routes red <title> to the JS/TS case of that exact title ⟦criterion 3⟧
- [ ] A WRONG_TEST: name ending in … or ... matches the one JS/TS title it is a prefix of, and red prints the full title, for each of the two ellipsis forms ⟦criterion 4⟧
- [ ] A WRONG_TEST: name equal to the tail of the step's own test id, given as `<describe> <title>` or as `<describe> > <title>`, counts as the step's own case and answers revise ⟦criterion 5⟧
- [ ] A WRONG_TEST: name that is the exact title of a sibling JS/TS case routes red to that sibling even when it is also one word of the step's own test id ⟦criterion 5⟧
- [ ] On the repair path (#1932), a SUPERSEDED: line naming a JS/TS case by its title, quoted, is matched by the same rules and listed after repair <case> ⟦criterion 6⟧
- [ ] wrong-test-route.sh's header comment names the JS/TS test files it searches (*.test.* / *.spec.* over .js .jsx .ts .tsx .mjs .cjs, files under __tests__/, never .d.ts) and the quote forms it reads on a WRONG_TEST: line (backticks, double quotes, curly quotes, a test_\w+ name) ⟦diff-checked⟧ ⟦criterion 7⟧
