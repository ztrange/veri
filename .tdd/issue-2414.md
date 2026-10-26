# Plan for #2414 — merge-lock.sh gate refuses a --pid that is not a pid instead of running the command and exiting 0

- [x] merge-lock.sh gate refuses a --pid value that is not a positive integer: `gate --pid -- true`, `gate --pid abc -- true` and `gate --keep --pid 0 -- true` each exit 2, print the gate usage line on stderr, run no command and create no .tdd/ directory, pinned by small in-process cases for those three argument lists ⟦criterion 1⟧ ⟂ refactor pending
