### For a range changing a script under skills/tdd/scripts/ with no same-named suite, affected-suites.sh prints no path that does not exist on disk ⟦criterion 1⟧
- test-only | the #1011 case's inline "every printed line exists on disk" loop in affected-suites.test.sh could become a reusable `expect_all_exist` assertion beside `expect_suites`
