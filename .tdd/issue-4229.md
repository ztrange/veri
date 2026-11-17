# Plan for #4229 — PRD 035.5a2: a resume's baseline suite is counted as a stage

- [ ] `PREFLIGHT.md` step 3 wraps a resume's baseline run in `event.sh stage-start stage=baseline` and `event.sh stage-end stage=baseline status=<exit code> secs=<seconds>` (PF69) ⟦criterion 1⟧
