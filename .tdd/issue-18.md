# Plan for #18 — classify-bail.sh: deterministically classify a bail as system vs process

- [x] a killed-stuck or no-verdict cause classifies as system
- [x] a revise-exhausted cause classifies as process
- [ ] an unrecognised cause exits non-zero, never a silent or default classification
