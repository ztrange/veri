# Plan for #1488 — status.sh's scope line counts every bail event, not the bail that stands

- [x] status.sh's scope line and its --json scope `bailed` field count a run as bailed only when the run's standing end is a bail: a run that bailed, was resumed and bailed again counts bailed 1, and a run that bailed, was resumed and finished counts done 1 and bailed 0 — pinned by a case in tests/py/test_status.py ⟦criterion 1⟧ ⟂ refactor pending
