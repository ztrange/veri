# Plan for #4301 — preflight.run's fresh-setup phase is its own function and baseline_suite's resume and fresh paths are split

- [x] run() holds no setup call inline: it calls one named function holding the fresh-setup phase (check_environment, check_readiness, set_up), which returns the stop code or (worktree, fast tier command, issue body file) ⟦diff-checked⟧ ⟦criterion 1⟧
- [x] that fresh-setup function is the only caller of check_environment, check_readiness and set_up, each called once ⟦diff-checked⟧ ⟦criterion 2⟧
- [x] baseline_suite dispatches between a function for the saved-resume path (a saved full or fast record) and one for the fresh path, with no saved-record branch nested inside an else ⟦diff-checked⟧ ⟦criterion 3⟧
- [x] behaviour unchanged: preflight's stdout, exit codes, stage events and -preflight file are the same, every existing preflight case green unedited ⟦full-suite⟧ ⟦criterion 4⟧
