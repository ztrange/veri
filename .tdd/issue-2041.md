# Plan for #2041 — skill-edit-step.sh launches its author leaf without bypassPermissions, so the author can write nothing

- [x] Every author leaf skill-edit-step.sh launches through supervise.sh/run-leaf.sh carries the flag pair `--permission-mode bypassPermissions`, as SKILL.md's leaves do: with a stub `claude` recording its arguments, each author launch's recorded arguments include that pair ⟦criterion 1⟧
