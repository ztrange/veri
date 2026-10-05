# Plan for #964 — detach-command.sh wait exits 1 for a non-numeric max-seconds (abc), the code for a red command; bad arguments exit 2

- [x] through the detach-command.sh entry point, with a command started by `start` and still running, `wait <name> abc` exits 2, prints nothing on stdout, and prints the usage line on stderr ⟦criterion 1⟧
- [x] through the detach-command.sh entry point, with `.tdd/<name>.exit` already holding `0`, `wait <name> abc` exits 2 with the usage line on stderr and nothing on stdout, refused before the exit file is read ⟦criterion 2⟧
- [x] the existing assertions in skills/tdd/scripts/tests/detach-command.test.sh are left unmodified by the branch, and the omitted-max default of 60 seconds stays on the unchanged code path ⟦diff-checked⟧ ⟦criterion 3⟧
- [x] the existing detach-command.test.sh cases (wait with max 0 and 30, and the 0/1/2/3 answers) pass in the full suite ⟦full-suite⟧ ⟦criterion 3⟧
- [x] #959 has not landed, so the fix stays in the bash detach-command.sh and the branch adds no Python source to any bash file ⟦diff-checked⟧ ⟦criterion 4⟧
