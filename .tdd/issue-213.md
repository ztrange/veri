# Plan for #213 — SKILL.md contradicts itself on whether an interactive session is a place to run a conductor

- [x] SKILL.md's launch section presents interactive and print mode as a trade the operator picks per run: interactive can be steered and costs ~25,000 tokens a request more, print mode is that much cheaper and turns every question into a bail ⟦criterion 1⟧
- [x] No passage in SKILL.md says an interactive session is not where a run belongs while another says to pick interactive deliberately ⟦criterion 2⟧
- [x] The reason SKILL.md gives for preferring print mode is the ~25,000-token per-request harness cost measured in #207, and no passage gives the CLAUDECODE nested-session refusal as that reason ⟦criterion 3⟧
- [ ] SKILL.md still tells the operator, if a nested-launch guard fires, to run the conductor from a plain shell outside the session with claude -p "/tdd <n>", and skill-conductor-launch.test.sh stays green ⟦criterion 4⟧
