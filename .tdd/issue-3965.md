# Plan for #3965 — PRD 022.9: a veri module uses a bytecode cache only when it is the user's own

- [x] `pycache_prefix.py` creates an absent prefix directory with mode `0700` and uses it ⟦criterion 1⟧
- [x] it sets no prefix when the `VERI_PYCACHE` directory is group-writable ⟦criterion 2⟧
- [x] it sets no prefix when the `VERI_PYCACHE` directory is other-writable ⟦criterion 2⟧
- [x] it sets no prefix when the `VERI_PYCACHE` path is a symlink to a directory of the user's own ⟦criterion 2⟧
- [x] it sets no prefix when the `VERI_PYCACHE` directory is owned by another user ⟦criterion 2⟧
- [x] it sets no prefix when the default `${TMPDIR}/veri-pycache-<uid>` directory is group-writable ⟦criterion 2⟧
- [x] on a refusal veri's modules compile from source through the `FromSource` finder and one stderr line names the path and why ⟦criterion 3⟧
- [x] a prefix path that is a regular file is refused, not used
- [x] a prefix that cannot be created or read is refused, not a traceback
- [x] CLAUDE.md's bytecode-cache paragraph says the prefix is used only when the user's own and closed to others (CM160), graded ⟦criterion 4⟧
- [x] a prefix the caller exported as PYTHONPYCACHEPREFIX is checked too, and a planted .pyc there never runs (review)
