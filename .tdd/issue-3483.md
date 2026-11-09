# Plan for #3483 — A conductor killed by an API outage is not a bail, like a usage limit or sleep

- [x] ⟦skill-edit⟧ skills/vbail/SKILL.md: an API outage is handled like a usage limit ⟦criterion 1⟧
- [x] ⟦skill-edit⟧ operator/PRINCIPLES.md: P10 checks a silent exit for an API outage ⟦criterion 2⟧
- [x] stop-reason.sh prints `outage [<text>]`, not `unknown`, when the conductor log ends in an API-unreachable error, and its usage names the line ⟦criterion 3⟧
- [ ] ⟦skill-edit⟧ skills/vbail/SKILL.md: Classify first routes `outage` to the outage section ⟦criterion 4⟧
- [ ] ⟦skill-edit⟧ operator/PRINCIPLES.md: P10 defines an outage as vbail does ⟦criterion 6⟧
- [ ] ⟦skill-edit⟧ skills/vdev/SKILL.md: No closing comment checks for an API outage (after #3486 lands) ⟦criterion 5⟧
