### SKILL.md's Draft PR structural pass stages and commits `.tdd/issue-<n>-refactor-owed.md` after its `refactor-owed.sh applied` call records an applied transform, before the PR is readied ⟦criterion 1⟧
- test-only | skill-structural-pass.test.sh's #980 case recomputes `offset "$applied_phrase" "$pass_text"`, which the #952 case already computed; the two cases could share that one offset
