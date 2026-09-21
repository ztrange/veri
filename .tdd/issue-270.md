# Plan for #270 — Seventeen scripts exit 1, not 2, on a missing argument: ${1:?usage} breaks the exit-code API

- [ ] Every script under skills/tdd/scripts/ that takes a required positional argument exits 2 with a usage line on stderr when it is missing ⟦criterion 1⟧
- [ ] The cross-suite guard fails, naming the offending script, when a script under skills/tdd/scripts/ exits with anything but 2 on a missing required argument ⟦criterion 2⟧
- [ ] The cross-suite guard fails, naming the offending script, when one still guards a required positional argument with a bare ${N:?…} expansion ⟦criterion 2⟧
