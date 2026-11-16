# Plan for #4058 — PRD 020.8: a stray file stops a skill-edit step before any author runs

- [x] a stray path present when an author attempt would run makes skill-edit-step.sh exit 2, naming it on stderr, launching no author and leaving unit, REQUIREMENTS.md and GRADED byte-identical ⟦criterion 1⟧
- [x] the issue-body file given, reported changed, does not stop the step: its author attempts run as before ⟦criterion 2⟧
- [x] the skill-edit-step.sh entry in skills/tdd/SCRIPTS.md states that exit 2 ⟦criterion 3⟧
