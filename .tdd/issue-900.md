# Plan for #900 — run-conductor.test.sh cases 31 and 32 sleep on the real clock through the ref-lock fetch retry

- [ ] run-conductor.sh waits between ref-lock fetch retries for the interval VERI_FETCH_RETRY_SLEEP names, so a run with VERI_FETCH_RETRY_SLEEP=0 retries a locked fetch without waiting on the real clock ⟦criterion 1⟧
- [ ] with VERI_FETCH_RETRY_SLEEP unset, run-conductor.sh still waits 1 s between ref-lock fetch retries, pinned by a case that records the interval each wait was given ⟦criterion 2⟧
- [ ] cases 31 and 32 of tests/run-conductor.test.sh exercise the ref-lock retry path with no real sleep, and their assertions are unchanged ⟦diff-checked⟧ ⟦criterion 1⟧
