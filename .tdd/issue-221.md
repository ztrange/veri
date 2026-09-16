# Plan for #221 — run-conductor.sh passes SKILL.md as argv, so its leading --- is parsed as an option and no conductor ever starts

- [x] run-conductor.sh launches successfully when the procedure's first line is the frontmatter fence, with the whole procedure reaching the binary
- [ ] The test suite fails if the procedure is passed as an argv element whose first character is a dash
- [ ] Everything else the header promises is unchanged: the VERI_* tunables pass through, the eight session handles are unset, stream-json and bypassPermissions are still on the command line
