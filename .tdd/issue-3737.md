# Plan for #3737 — Cover the behaviour #3711 refactors

- [ ] update_veri.py's git() runs git against the clone holding the scripts directory (two levels above update_veri.py, through realpath), so a case pins that root and goes red when git() uses root = "/nonexistent-xyz" instead; no production change ⟦criterion 1⟧
