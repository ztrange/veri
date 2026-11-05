# Plan for #2895 — PRD 017.1: wrong-test-route finds cases and helpers through the test-case reader

- [ ] Move the case-finding patterns of wrong_test_route.py's `_exists` (the Python `def`, Go `func` and JS title-via-`CALL` patterns) behind case_reader.py, with the same answers and no test edited: `git grep -nE '"(def|func) \(|CALL' -- 'skills/tdd/scripts/veri/wrong_test_route.py'` prints nothing ⟦criterion 1⟧
- [ ] Move the helper-finding patterns of wrong_test_route.py's `_fixture` (the Python `^def`, Go `^func` and JS `function`/`const … =>` helper patterns) behind case_reader.py, with the same answers and no test edited: `git grep -nE '"\^?(def|func) |function\\s|CALL' -- 'skills/tdd/scripts/veri/wrong_test_route.py'` prints nothing ⟦criterion 1⟧
- [ ] At the branch tip `git grep -l 'case_reader' -- 'skills/tdd/scripts/veri/wrong_test_route.py'` prints that file: wrong_test_route.py reads cases and helpers through case_reader ⟦diff-checked⟧ ⟦criterion 2⟧
