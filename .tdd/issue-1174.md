# Plan for #1174 — A conductor's or leaf's cleanup kills processes by pattern machine-wide, and can stop other live runs

- [x] Every built developer prompt, through the shared develop-prompt text, tells the leaf it signals only processes it started, by the pid it recorded when it started them, never by name or pattern (`pkill`, `killall`, `kill $(pgrep …)`), and that an experiment's processes and leaf names carry the `exp-` prefix no live run uses ⟦criterion 1⟧
- [x] `skills/tdd/SKILL.md` tells the conductor it signals only processes it started, by the pid it recorded when it started them, never by name or pattern (`pkill`, `killall`, `kill $(pgrep …)`), and that an experiment's processes and leaf names carry the `exp-` prefix no live run uses ⟦criterion 1⟧ ⟂ refactor pending
