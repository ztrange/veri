# Plan for #680 — parallel-conductors.test.sh's #645 cases synchronise on files and FIFOs, not sleeps

- [x] the split-event case's stub delivers its one assistant event in two separate writes with no `sleep` between them, the second write held back by a file or FIFO the stub waits on without a time bound, and the case still asserts exactly one `context 7 53438` line ⟦criterion 2⟧
- [x] `stub_waits`' `await_context` waits for its `context <issue> <tokens>` line with no `sleep` and no iteration cap, returning only once that line has arrived ⟦criterion 1⟧
- [x] `stub_waits`' `heartbeats` carries no `sleep`, and the stop, under, beside and VERI_PARALLEL=1 cases that call it still assert the same expected marks, the stubs waiting on a file or FIFO rather than on elapsed time for the launcher to stop them ⟦criterion 1⟧
- [x] the stop case and the VERI_PARALLEL=1 one case wait for the stopped stub to be gone with no `sleep` and no iteration cap before reading its marks ⟦criterion 1⟧
- [x] the beside case's #8 stub waits for #7's stub to be gone with no `sleep` and no iteration cap, and the case still asserts `before-result-7`, `8-outlived-7`, `end-8` ⟦criterion 1⟧
- [x] the again case's stub, after its step-done result, holds on a file or FIFO rather than `sleep 2`, and the case still asserts launches 7, 7, 8 and one `restarted 7` line ⟦criterion 1⟧ ⟂ refactor pending
- [ ] each case #645 added still asserts what it asserts today, with the same expected lines ⟦full-suite⟧ ⟦criterion 3⟧
- [ ] `parallel-conductors.sh` is unchanged — `git diff origin/main -- skills/tdd/scripts/parallel-conductors.sh` empty ⟦human-owed⟧ ⟦criterion 4⟧
- [ ] every case in `parallel-conductors.test.sh` that #645 did not add is unchanged ⟦human-owed⟧ ⟦criterion 5⟧
