# Plan for #161 — A leaf launched with nohup dies when the Bash call that launched it ends

- [x] A process started through `detach-leaf.sh` keeps running, and writes its completion file, after a TERM is sent to the process group of the shell that launched it
- [ ] Every developer and verifier leaf launch in SKILL.md goes through the launcher and none uses nohup, pinned by a suite in `make test` that fails when a launch line does not
- [ ] The *Launching a leaf* section of SKILL.md says why nohup alone is not enough — it survives a hang-up but not a signal to the launching call's process group
- [ ] CLAUDE.md's stated script and suite counts match the scripts and suites on disk
