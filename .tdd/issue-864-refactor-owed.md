### SKILL.md preflight step 0.2 names `gh api user` as the GitHub check, and says a non-zero exit from it stops the run as a preflight failure ⟦criterion 1⟧
- test-only | hoist the literal 'preflight' in skill-preflight-launchable.test.sh's #864 case into a named variable beside `nonzero`
