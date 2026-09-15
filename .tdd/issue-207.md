# Plan for #207 — A conductor pays ~25k a request for a harness it never uses

- [x] `run-conductor.sh <issue>` launches one conductor as `claude -p` with a streamed event output
- [x] The eight inherited session handles are absent from the child's environment; `VERI_*` tunables are not
- [x] The child's exit status is the script's
- [x] `SKILL.md` says which launch modes exist and that a print-mode conductor cannot be asked a question mid-run
- [x] `CLAUDE.md`'s script and suite counts move with the added files
