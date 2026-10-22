# Plan for #2012 — The Popen-command helper's guards: pin that both call it, read args once, and import it one way

- [x] network_guard, small_case_guard and unit/test_popen_command.py reach popen_command through one module path, so one module object is loaded: a unit-tier case (no process) asserts the helper module each guard uses is the same object as the one test_popen_command.py imports ⟦criterion 3⟧
- [x] A unit-tier case (no process) fails if either network_guard or small_case_guard stops calling the popen_command helper and keeps its own copy of the Popen-args-to-basename lines, one assertion per guard, watched red by reverting one guard to its own copy; no production change ⟦criterion 1⟧
- [x] network_guard reads `args` once, so an iterator `args` such as iter(["gh"]) gets network_guard's own refusal, the same outcome as the list ["gh"], instead of an IndexError: a unit-tier case (no process) ⟦criterion 2⟧
- [x] small_case_guard reads `args` once, so an iterator `args` such as iter(["python3", "<path under veri/>"]) gets the same outcome as the equivalent list (allowed), not a refusal: a unit-tier case (no process) ⟦criterion 2⟧ ⟂ refactor pending
- [ ] small_case_guard raises its own TypeError for a list `args` holding a non-str word, ["ls", 5], as it did before #1894, instead of passing it through: a unit-tier case (no process) ⟦criterion 2⟧
