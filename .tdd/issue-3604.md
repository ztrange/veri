# Plan for #3604 — status.sh --recover dies on one torn journal line

- [x] With a journal under $VERI_HOME/runs holding one torn line among whole ones, `status.sh --recover` (through `journals()` in `status.py`) exits its normal code and reads every whole event of that journal and of every other journal instead of dying with a JSONDecodeError; this case is the go-red guard, its Red run against the code without the skip being the evidence it goes red when the skip is removed ⟦criterion 1⟧
- [x] When `journals()` in `status.py` skips a torn line it writes one stderr line naming the journal file and the torn line's line number ⟦criterion 1⟧ ⟂ refactor pending
- [ ] `append_once()` in `event.py` exits 2 with a message on stderr when `os.write` returns fewer bytes than `len(data)`, pinned by a case faking a short `os.write` ⟦criterion 2⟧
