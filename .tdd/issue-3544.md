# Plan for #3544 — add-ledger-step.sh treats a step that only mentions the skill-edit marker in prose as a skill-edit step, and a missing unit file raises FileNotFoundError

- [ ] add-ledger-step.sh adds a new step whose prose mentions the skill-edit marker (with a backticked path in its prose) but does not carry it in its trailing tag run as a plain step, exiting 0, with no unit or requirements-list lookup ⟦criterion 1⟧
- [ ] add-ledger-step.sh refuses a new step carrying the skill-edit marker as its trailing tag whose unit file does not exist with exit 2 and a stderr message naming the unit, with no Python exception text (the case must go red when the missing-unit guard is removed and the missing file raises again) ⟦criterion 2⟧
