# Plan for #504 — refactor debt is worked before the PR is ready, and the overflow is filed

- [x] refactor-owed.sh list prints each recorded structural candidate once, most valuable first: a candidate recorded under more steps before one recorded under fewer, ties kept in the order they were recorded ⟦criterion 1⟧
- [x] SKILL.md's structural pass takes the candidates in the order `refactor-owed.sh list` prints them and names that order as most valuable first ⟦criterion 1⟧
- [x] refactor-overflow.sh <n> <owed-file> <reached> files one issue whose title and body name the parent issue #<n> and whose body lists every candidate `refactor-owed.sh list` prints after the first <reached>, prints the new issue's URL and exits 0 ⟦criterion 2⟧
- [x] refactor-overflow.sh files nothing — no `gh` call — and exits 3 with empty stdout when the owed file is missing or holds no candidate, or when <reached> covers every candidate; it exits 2 on a missing or non-numeric argument ⟦criterion 3⟧
- [x] refactor-overflow.sh sends no label with the issue it files, makes no call that labels or edits the parent issue, and writes no file into the repository ⟦criterion 5⟧
- [x] SKILL.md's structural pass, when it ends with `stopped=budget-spent`, runs refactor-overflow.sh with the number of candidates it took up and puts the filed issue's URL in the PR body; when it ends with `candidates-done` or `nothing-structural` it files nothing ⟦criterion 2⟧ ⟂ refactor pending
- [ ] SKILL.md's Draft PR body still carries `refactor-owed.sh render`'s `## Refactor owed` section after the structural pass has run ⟦criterion 4⟧
- [ ] SKILL.md states that the overflow filing applies no label to the parent issue and commits no standing debt file to the repository ⟦criterion 5⟧
