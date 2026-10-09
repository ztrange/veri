### add-ledger-step.sh given `--criterion <k>` tags every inserted line `⟦criterion k⟧`, whatever criterion the anchor step carries ⟦criterion 1⟧
- test-only | extract the suite-wide `monkeypatch.delenv("VERI_STEP_GROWTH", raising=False)` + `ledger.write_bytes(LEDGER)` setup in `test_add_ledger_step.py` into a fixture
### add-ledger-step.sh given `--criterion <k>` for a k no ledger step carries exits 2 with one stderr line naming k and leaves the ledger byte-identical ⟦criterion 3⟧
- test-only | `test_add_ledger_step.py` — the new refusal test repeats the `delenv("VERI_STEP_GROWTH")` + `ledger = tmp_path / "issue-42.md"` + `write_bytes(LEDGER)` setup the earlier `--criterion` tests in this file also use; it could become a fixture
