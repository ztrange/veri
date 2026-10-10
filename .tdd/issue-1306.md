# Plan for #1306 — run_conductor.py's ref-lock retry misses git 2.53's wording

- [x] A fetch of origin whose stderr is git 2.53's held-ref-lock wording (`error: fetching ref refs/remotes/origin/master failed: reference already exists`), fed in-process as the fetch's stderr, is retried through the sleep exactly as a `cannot lock ref` fetch is — at most 60 fetches and 59 sleeps — then refused with exit 2 ⟦criterion 1⟧
- [x] When a fetch refused after spending its retries failed on git 2.53's `reference already exists` wording, the refusal on stderr names the ref lock as the cause, as the `cannot lock ref` wording already does ⟦criterion 1⟧
- [x] A fetch of origin failing with neither ref-lock wording is still refused at once — exit 2 after one fetch and no sleep — and its refusal does not name the ref lock ⟦criterion 1⟧
