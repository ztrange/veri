# Plan for #4856 — preflight baseline execs a compound test command without a shell: '&&' reaches the tool as an argument

- [x] preflight's fast and full baselines start a compound command as `sh -c <command>` through detach-command.sh ⟦criterion 1⟧ ⟦criterion 2⟧
- [x] branch_gate.py start(), pr_prepare.py tip_suite() and ready_check.py's tier run start a compound command as `sh -c <command>` ⟦criterion 3⟧
- [x] make test exits 0 ⟦full-suite⟧ ⟦criterion 4⟧
