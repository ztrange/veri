# Plan for #4052 — PRD 025.17: one helper writes a stub script

- [x] stub_script.write_stub(path, body) writes `#!/bin/sh\n` then body to path, sets mode 0755 and returns path ⟦criterion 1⟧
- [x] test_local_stub_scripts.py fails naming an unlisted file under tests/py/ holding a string literal starting `#!/bin/sh`, read with ast, stub_script.py exempt, against a sorted one-per-line list with reasons ⟦criterion 2⟧
- [x] test_local_stub_scripts.py fails naming a listed file that no longer holds such a literal ⟦criterion 2⟧
