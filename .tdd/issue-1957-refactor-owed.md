### An it(…) or test(…) call inside a /* … */ block comment is not a case: a WRONG_TEST: naming only its title answers revise ⟦criterion 2⟧
- test-only | extract a shared helper in test_wrong_test_route.py for the repeated "write foo.test.ts, write the report, run the CLI" setup in the 1957 cases
### A WRONG_TEST: name ending in … or ... matches the one JS/TS title it is a prefix of, and red prints the full title, for each of the two ellipsis forms ⟦criterion 4⟧
- extract the ellipsis-prefix and JS title-pattern construction in `_exists` into a helper (no duplication, so not applied here)
### A WRONG_TEST: name equal to the tail of the step's own test id, given as `<describe> <title>` or as `<describe> > <title>`, counts as the step's own case and answers revise ⟦criterion 5⟧
- split `_exists` into per-language matchers (py def, JS/TS title regex, `.test.sh` name) — moves behaviour, not duplication removal
