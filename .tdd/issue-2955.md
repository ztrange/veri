# Plan for #2955 — detach-command.sh start strips a trailing `--alone <x>` from the command it runs

- [x] `detach-command.sh start <name> <cmd…> --alone <x>` runs the command with `--alone <x>` among its arguments, unchanged: `detach_command.py` parses `--alone` only when `argv[0] == "wait"` ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `wait … --alone <x>` still behaves as #2912 pins, and the existing cases stay green ⟦full-suite⟧ ⟦criterion 2⟧
