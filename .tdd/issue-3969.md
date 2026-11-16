# Plan for #3969 — PRD 022.3: the dispatcher reads a run's outcome only from a trusted comment

- [x] github.trusted_comment trusts a comment whose author_association is OWNER or COLLABORATOR and no other association, whatever its body says (a stranger's comment carrying veri's exact marker text, an edited one, a bot that is not veri's) ⟦criterion 1⟧
- [x] a comment whose user.login is the authenticated gh user's is trusted whatever its association (a MEMBER) ⟦criterion 1⟧
- [x] the authenticated login is read with gh api user at most once per process ⟦criterion 1⟧
- [x] with the authenticated login unreadable, the association alone answers and the caller is not stopped ⟦criterion 2⟧
- [x] a comment whose author cannot be read (no user, a null user, no login, not an object) or whose association GitHub reports and the rule does not list is not trusted
- [x] dispatch.exit_line reads trusted comments only: an untrusted ### ✅ Done after a trusted ### ⛔ Bailed prints bail <n> ⟦criterion 3⟧
- [ ] a thread whose only outcome comment is untrusted prints silent-exit <n> ⟦criterion 4⟧
- [ ] comment_bodies reads every page: a trusted outcome comment on page 2 decides the line ⟦criterion 5⟧
- [ ] the dispatch.sh entry of SCRIPTS.md says the outcome line is read from trusted comments only, naming the rule ⟦criterion 6⟧
