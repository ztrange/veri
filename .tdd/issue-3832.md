# Plan for #3832 — Resetter cannot resume a coordinator it cannot reach by name

- [x] The *Resetter* section of `skills/vdev/SKILL.md` tells a resetter whose send to the dev session by session name fails (the name does not resolve, or `ListAgents` does not list it) to look the dev session up in the linked-session list, or use the session id it was started from, and send by that id, notifying the operator only when that send also fails (row D139) ⟦skill-edit⟧ ⟦criterion 1⟧
- [ ] The *Resetter* section of `skills/vdev/SKILL.md` tells the resetter to pass `--lane <lane>` to every `$S/reset-wait.sh` call (`marker`, `recovered`) whenever the dev session runs in a lane, the unlaned form being for a dev session with no lane only (row D140) ⟦skill-edit⟧ ⟦criterion 2⟧
