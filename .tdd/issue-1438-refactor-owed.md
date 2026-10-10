### With no user.name/user.email in any git config, preserve-attempt.sh still writes the snapshot ref under refs/veri/attempts/<issue>/<step>/<phase>-<attempt> and exits 0 ⟦criterion 1⟧
- test-only | drop the double blank line before the #1438 case at skills/tdd/scripts/tests/preserve-attempt.test.sh:372
