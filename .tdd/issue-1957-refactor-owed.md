### An it(…) or test(…) call inside a /* … */ block comment is not a case: a WRONG_TEST: naming only its title answers revise ⟦criterion 2⟧
- test-only | extract a shared helper in test_wrong_test_route.py for the repeated "write foo.test.ts, write the report, run the CLI" setup in the 1957 cases
### A WRONG_TEST: name ending in … or ... matches the one JS/TS title it is a prefix of, and red prints the full title, for each of the two ellipsis forms ⟦criterion 4⟧
- extract the ellipsis-prefix and JS title-pattern construction in `_exists` into a helper (no duplication, so not applied here)
### A WRONG_TEST: name equal to the tail of the step's own test id, given as `<describe> <title>` or as `<describe> > <title>`, counts as the step's own case and answers revise ⟦criterion 5⟧
- split `_exists` into per-language matchers (py def, JS/TS title regex, `.test.sh` name) — moves behaviour, not duplication removal
### A WRONG_TEST: name that is the exact title of a sibling JS/TS case routes red to that sibling even when it is also one word of the step's own test id ⟦criterion 5⟧
- split `_exists` in `wrong_test_route.py` into a JS title-pattern builder (ellipsis prefix, `.only`/`.skip`/`.each`) and the directory walk
- `_exists` returns either `True` or a title string, so `route` has to unwrap it with `case if found is True else found`; returning the matched title in both cases would remove the unwrapping
applied | e2df8f99de5886ab009dcd0b5770a4bee9fef99d | split `_exists` in `wrong_test_route.py` into a JS title-pattern builder (ellipsis prefix, `.only`/`.skip`/`.each`) and the directory walk
