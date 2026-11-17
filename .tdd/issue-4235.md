# Plan — #4235 the metrics hold the conductor's spend per phase

- [ ] conductor.by_phase attributes each timed turn to the innermost leaf or stage window holding it, else between; an untimed one to untimed; turns sum to conductor.turns (MP1, MP2, MP3)
- [ ] no stream log gives conductor.by_phase null (MP4)
- [ ] PUBLISHED.md states by_phase, its keys and that its costs are estimates (MP5)
