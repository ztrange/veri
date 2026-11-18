# Plan for #4305 — wrong_test_route._resolves reuses one per-file match instead of repeating it

- [x] `_resolves` accepts a Python/Go definition, a JS title written whole and a JS name cut at `…` that matches a longer title, and rejects a name no file defines ⟦criterion 2⟧
- [x] `file_defines` accepts a Python/Go definition and a JS title written whole, and rejects a JS name cut at `…` and a name no file defines ⟦criterion 3⟧
- [ ] `_resolves` asks case_reader's shared per-file match instead of calling `defined_name` or `live_titles` inline ⟦criterion 1⟧
