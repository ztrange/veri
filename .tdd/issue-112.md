# Plan for #112 — A bug's Red is a reproduction: the test must fail for the reported reason and stays as the regression test

- [x] capture-spec.sh writes the blind spec with a Bug section carrying what happened, expected, steps to reproduce and environment when the issue carries the bug label ⟦criterion 1⟧
- [x] capture-spec.sh writes a spec with no Bug section when the issue does not carry the bug label ⟦criterion 1⟧
- [x] SKILL.md captures the blind spec through capture-spec.sh rather than a bare gh issue view ⟦criterion 1⟧
- [x] build-develop-prompt.sh red emits its reproduction paragraph only when the spec has a Bug section, with its parameters unchanged ⟦criterion 2⟧
- [x] build-verify-prompt.sh red emits its reproduction paragraph, requiring the observed failure to match what happened, only when the spec has a Bug section, with its four parameters unchanged ⟦criterion 2⟧
- [x] the develop-red reproduction paragraph tells the leaf to name the bug test so it carries the issue number ⟦criterion 3⟧
- [x] SKILL.md gives a bug step's green commit a fix: subject and a bug run's PR title a fix: prefix ⟦criterion 3⟧ ⟂ refactor pending
