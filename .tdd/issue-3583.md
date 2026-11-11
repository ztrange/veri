# Plan for #3583 — role-state.sh add timed-n accepts text dispatch.sh cannot parse, stalling dispatch

- [ ] `role-state.sh <role> add timed-n <text>` with a text dispatch's timed-n parser cannot parse (e.g. `4 until weekly usage reset ~2026-11-10 evening`) exits 2, names the `<n> until <ISO-8601 datetime>` form on stderr, and writes nothing to the state file ⟦criterion 1⟧
- [ ] `role-state.sh <role> add timed-n` with a well-formed `<n> until <ISO datetime>` text still appends the `timed-n` line to the state file and prints its id ⟦criterion 2⟧
- [ ] `role_state.py` and `dispatch.py` call one shared timed-n parse function, with no second copy of the `<n> until <ISO datetime>` format in either module ⟦diff-checked⟧ ⟦criterion 3⟧
- [ ] The timed-n refusal guard, broken on purpose (validation removed), goes red ⟦human-owed⟧ ⟦criterion 4⟧
