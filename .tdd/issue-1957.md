# Plan for #1957 — wrong-test-route.sh recognises Vitest/JS/TS test cases, quoted and ellipsis-cut names

Every case is a small in-process case in skills/tdd/scripts/tests/py/unit/test_wrong_test_route.py, driving wrong_test_route.main through run_cli against a throwaway repo under tmp_path (no process, no git).

- [x] A WRONG_TEST: or SUPERSEDED: line indented by one, two or three spaces is read as prose, not a route line: the existing #1865 case that treats a two-space-indented SUPERSEDED: line as real is changed to expect revise, for one, two and three spaces ⟦criterion 8⟧
- [x] A WRONG_TEST: line indented by one, two or three spaces naming an existing sibling case answers revise, not red ⟦criterion 8⟧
- [x] A WRONG_TEST: naming in backticks the exact title of an it('…') call in a foo.test.ts file routes red <title> ⟦criterion 1⟧
- [x] A WRONG_TEST: naming the title of an it(…) call routes red when the file is a *.test.* or *.spec.* file over each of .js .jsx .ts .tsx .mjs .cjs ⟦criterion 1⟧
- [x] A WRONG_TEST: naming the title of an it(…) call routes red when the call sits in a .js or .ts file under a __tests__/ directory whose name carries no .test or .spec ⟦criterion 1⟧
- [x] A .d.ts file is never a test file: a WRONG_TEST: naming the title of an it(…) call found only in foo.test.d.ts or __tests__/types.d.ts answers revise ⟦criterion 1⟧
- [x] A WRONG_TEST: naming the title of an it(…) call found only in a non-test source file (config.ts, src/testing/config.js) answers revise ⟦criterion 1⟧
- [x] A WRONG_TEST: naming the exact title of a test(…) call in a JS/TS test file routes red <title> ⟦criterion 2⟧
- [x] The .only and .skip forms of it(…) and test(…) (it.only, it.skip, test.only, test.skip) are cases: a WRONG_TEST: naming their title routes red <title> ⟦criterion 2⟧
- [x] The call after an .each([...]) head and after an .each`…` tagged-template head (it.each, test.each) is a case: a WRONG_TEST: naming its title routes red <title> ⟦criterion 2⟧
- [x] An it(…) or test(…) call commented out with // is not a case: a WRONG_TEST: naming only its title answers revise ⟦criterion 2⟧
- [x] An it(…) or test(…) call inside a /* … */ block comment is not a case: a WRONG_TEST: naming only its title answers revise ⟦criterion 2⟧
- [x] A case name in double quotes on the WRONG_TEST: line is a candidate: it routes red <title> to the JS/TS case of that exact title ⟦criterion 3⟧
- [x] A case name in curly quotes (“…”) on the WRONG_TEST: line is a candidate: it routes red <title> to the JS/TS case of that exact title ⟦criterion 3⟧
- [x] A WRONG_TEST: name ending in … or ... matches the one JS/TS title it is a prefix of, and red prints the full title, for each of the two ellipsis forms ⟦criterion 4⟧
- [x] A WRONG_TEST: name equal to the tail of the step's own test id, given as `<describe> <title>` or as `<describe> > <title>`, counts as the step's own case and answers revise ⟦criterion 5⟧
- [x] A WRONG_TEST: name that is the exact title of a sibling JS/TS case routes red to that sibling even when it is also one word of the step's own test id ⟦criterion 5⟧
- [x] On the repair path (#1932), a SUPERSEDED: line naming a JS/TS case by its title, quoted, is matched by the same rules and listed after repair <case> ⟦criterion 6⟧
- [x] wrong-test-route.sh's header comment names the JS/TS test files it searches (*.test.* / *.spec.* over .js .jsx .ts .tsx .mjs .cjs, files under __tests__/, never .d.ts) and the quote forms it reads on a WRONG_TEST: line (backticks, double quotes, curly quotes, a test_\w+ name) ⟦diff-checked⟧ ⟦criterion 7⟧
- [x] A SUPERSEDED: line naming a JS/TS case by a cut name ending in … (SUPERSEDED: "rejects an empty n…") prints red <the full title>, never the cut name ⟦criterion 9⟧
- [x] A WRONG_TEST: cut name ending in … whose expansion is the title of the step's own case answers revise, never red <own case>: the own-case check runs on the expanded title ⟦criterion 10⟧
- [x] A WRONG_TEST: naming a bare … whose expansion is the title of the step's own case answers revise, never red <own case> ⟦criterion 10⟧
- [x] A WRONG_TEST: cut name ending in … that is a prefix of more than one JS/TS title in the searched files answers revise, never red over the first match ⟦criterion 11⟧
- [x] A live it(…) call on a line below a // comment on an earlier line is a case: a WRONG_TEST: naming its title routes red <title> (holds today; pinned) ⟦criterion 12⟧
- [x] A JS/TS test file holding only emit('<title>') and no it(…) or test(…) call has no case of that title: a WRONG_TEST: naming it answers revise (holds today; pinned) ⟦criterion 12⟧
- [x] A file __tests__/notes.md holding it('<title>') is not a test file: a WRONG_TEST: naming that title answers revise (holds today; pinned) ⟦criterion 12⟧
- [x] A WRONG_TEST: name equal to the title tail of the step's own test id written <describe> > <title> answers revise (holds today; pinned) ⟦criterion 12⟧
- [x] A MISSING_TEST: line indented by one, two or three spaces is read as prose, by the same rule as WRONG_TEST: and SUPERSEDED: lines: the report answers revise, never missing <behaviour> (holds today; pinned) ⟦criterion 13⟧
- [x] A WRONG_TEST: cut name in backticks (`doesn…`) expands to the title of it("doesn't crash on null"), a double-quoted title holding a single quote: red prints doesn't crash on null, the title matched up to the quote that opened it ⟦criterion 14⟧ ⟂ refactor pending
- [ ] A WRONG_TEST: cut name in backticks (`says…`) expands to the title of it('says "hi" loudly'), a single-quoted title holding double quotes: red prints says "hi" loudly, the title matched up to the quote that opened it ⟦criterion 14⟧
- [ ] A lone SUPERSEDED: cut name ending in … that expands to the title of the step's own JS/TS case, on a report whose WRONG_TEST: names no case that routes, answers revise, never red <own case>: the own-case check runs on the expanded SUPERSEDED: title ⟦criterion 15⟧
- [ ] A SUPERSEDED: cut name ending in … that expands to the title of the step's own JS/TS case, on the repair path (WRONG_TEST: names the step's own recorded case), answers revise, never a repair in which the own case supersedes itself ⟦criterion 15⟧
- [ ] .tdd/issue-1957-refactor-owed.md's applied rows cite, for the helpers _js_title_pattern and _cut_prefix, the commits on the rebased branch that applied them, each with its commit subject, so every cited sha resolves on the branch (git cat-file -e) and names that helper's commit ⟦diff-checked⟧ ⟦criterion 16⟧
