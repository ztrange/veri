# Plan for #173 — A supervisor that dies writes no completion file, so wait-leaf.sh answers 'still running' forever

- [x] wait-leaf.sh exits 2, well before max-seconds, with a diagnostic on stderr naming the leaf and the dead pid, when no completion file exists and the pid file names a process that has exited
- [x] wait-leaf.sh treats a recorded pid that is alive but is not a supervise.sh for that name (pid reuse) as a dead supervisor
- [x] wait-leaf.sh still exits 3 while the recorded supervise.sh for that name is alive, and a missing pid file is not dead
- [x] wait-leaf.sh returns the recorded code when the completion file lands just before the supervisor exits
- [x] supervise.sh records its own pid in .tdd/<name>.pid before it launches the leaf ⟂ refactor pending
- [ ] supervise.sh sent TERM, INT or HUP writes 2 to its completion file, exits 2 and leaves no leaf process behind
- [ ] A pid file left by an earlier leaf of the same name cannot end a later wait early: SKILL.md's launch lines clear .tdd/<name>.pid together with .tdd/<name>.exit
- [ ] SKILL.md says a 2 from wait-leaf.sh also means the supervisor died without recording a status, and that it takes the killed-stuck branch like any other 2
