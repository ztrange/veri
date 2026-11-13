# Plan for #3752 — role-state.sh add exits 2 with a ValueError once the state file holds a coordinator= value containing a space

- [x] With a state file holding the line `coordinator=veri coord` and one `message 1 <ts> <text>` item, `role-state.sh <role> add message x` prints `2` and exits 0: `add` numbers items only from list lines; an in-process unit case driving the CLI with `run_cli`, faking nothing but the state file ⟦criterion 1⟧
- [x] With a state file holding the line `coordinator=veri coord` and no list line at all, `role-state.sh <role> add message x` prints `1` and exits 0; an in-process unit case driving the CLI with `run_cli`, faking nothing but the state file ⟦criterion 2⟧
