# Plan for #1169 — run-conductor.test.sh can go red after make unit: its skill copy picks up pytest caches

- [x] run-conductor.test.sh's skill copy (loose_skill) carries only the files git tracks under skills/tdd, so an untracked or ignored file there — a pytest cache, a __pycache__ — never reaches the scratch skill repo and the suite's result does not depend on whether make unit ran first ⟦criterion 1⟧ ⟂ refactor pending
