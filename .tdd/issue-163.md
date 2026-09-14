# Plan for #163 — Leaf events carry an empty issue and step, and no run ever writes a usage event

- [x] supervise.sh's launch and exit events carry VERI_ISSUE and VERI_STEP from its environment
- [x] verify.sh's verdict event carries VERI_ISSUE and VERI_STEP from its environment
- [x] SKILL.md's developer and verifier launch lines set VERI_ISSUE and VERI_STEP ⟂ refactor pending
- [ ] a supervised leaf whose log ends in a result record leaves exactly one usage event
- [ ] a killed leaf leaves no usage event and supervise.sh still exits 2 and writes 2 to its completion file
- [ ] a failing harvester leaves supervise.sh's exit code and completion file unchanged
