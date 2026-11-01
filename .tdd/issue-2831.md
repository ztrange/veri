# Plan for #2831 — skills/tdd/.on-demand names tdd, not vfile

- [x] `skills/tdd/.on-demand` contains no `vfile`, and any `ln -s` path it shows ends in `skills/tdd`; a case in `skills/tdd/scripts/tests/py/unit/test_install_links.py` pins it and goes red when `vfile` is put back ⟦criterion 1⟧ ⟂ refactor pending
