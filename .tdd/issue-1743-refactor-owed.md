### claims on a unit with a second `| ID | Requirement | Why |` table after a blank line exits 2, prints nothing on stdout and names the second table's header line on stderr ⟦criterion 3⟧
- hoist the per-iteration `fail` closure in `claims` to a module-level helper taking path and line number
