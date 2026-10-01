# Plan for #627 — the back-to-back JSON decoder lives in one module instead of five copies

- [x] Move Function: `documents` leaves `solvable-issues.sh` for a new `skills/tdd/scripts/lib/json_documents.py`, written complete (`documents(text)` — the documents in order, unflattened, skipping whitespace before each and at the end — and `items(text)` — their elements as one list), and `solvable-issues.sh` imports it via `PYTHONPATH` set to `lib`. Predicate: `test -f skills/tdd/scripts/lib/json_documents.py && ! grep -q raw_decode skills/tdd/scripts/solvable-issues.sh` ⟦criterion 2⟧
- [x] Replace Inline Code with Function Call in `invisible-work.sh`: its copy of `documents` goes, and it imports `json_documents`. Predicate: `! grep -q raw_decode skills/tdd/scripts/invisible-work.sh` ⟦criterion 2⟧
- [x] Replace Inline Code with Function Call in `workqueue.sh`: its inline decode loop goes, and it imports `json_documents`. Predicate: `! grep -q raw_decode skills/tdd/scripts/workqueue.sh` ⟦criterion 2⟧
- [x] Replace Inline Code with Function Call in `parallel-conductors.sh`: its inline decode loop goes, and it imports `json_documents`. Predicate: `! grep -q raw_decode skills/tdd/scripts/parallel-conductors.sh` ⟦criterion 2⟧
- [ ] Replace Inline Code with Function Call in `wait-ci.sh`: its `docs(text)` goes from both programs built on `$json_docs`, and they import `json_documents`'s `documents`. Predicate: `! grep -q raw_decode skills/tdd/scripts/wait-ci.sh` ⟦criterion 2⟧
- [ ] `lib/json_documents.py` is the only file under `skills/tdd/scripts/`, tests aside, that calls `raw_decode`, recorded once the full suite is green after step 5 ⟦full-suite⟧ ⟦criterion 1⟧
- [ ] no commit on the branch changes a test file (each transform is gated by `transform-touches-tests.sh`), recorded once the full suite is green ⟦full-suite⟧ ⟦criterion 3⟧
- [ ] `make test` is green ⟦full-suite⟧ ⟦criterion 4⟧
