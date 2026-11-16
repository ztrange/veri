# Plan for #3967 — PRD 022.21: make install-dev installs only hash-checked packages

- [x] requirements-dev.txt lists every package the direct pins of requirements-dev.in pull in, each with == and a sha256 hash, under a header naming the command that regenerates it ⟦criterion 1⟧
- [x] make install-dev exits non-zero on a lock line missing its hash ⟦criterion 2⟧
- [x] ci.yml's cache-dependency-path still names requirements-dev.txt ⟦criterion 3⟧
- [x] CLAUDE.md's make install-dev row says it installs the hash-checked lock ⟦criterion 4⟧
