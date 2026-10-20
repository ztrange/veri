# Plan for #1843 — mutation-parity.sh crashes (exit 2) when a bash case name contains '::'

- [x] mutation-parity.sh judges a pairs-table row whose suite is a bash suite (a path not ending in `.py`) and whose old case name contains `::` with the bash runner, so the row gets a verdict (proven/unproven/owed) and the check does not exit 2; pinned by a case ⟦criterion 1⟧ ⟂ refactor pending
- [ ] mutation-parity.sh still judges a pairs-table row whose suite is a `.py` file with the pytest runner, as today, so a pytest suite row keeps getting its verdict; pinned by a case ⟦criterion 2⟧
