# Plan for #111 — /tdd-fix files a bug with the headings veri reads, labels it bug, and offers to start the fix

- [x] skills/tdd-fix/SKILL.md exists as the /tdd-fix skill, taking an optional one-line description and asking only for what that line left out, in one short round ⟦criterion 1⟧
- [x] The issue body it files carries exactly the six headings the conductor reads — What happened, Expected, Steps to reproduce, Environment, Acceptance criteria, and Blocked by holding None ⟦criterion 1⟧
- [x] Each acceptance criterion it writes is one per manifestation, in the reproduction-fails-now-and-passes-after-the-fix shape ⟦criterion 1⟧
- [x] The issue is labelled bug and the opt-in label, ready-for-agent by default or ready-for-agent with a scope suffix when the user names one, creating the bug label when the repo lacks it ⟦criterion 2⟧
- [x] The skill asks one question before starting the fix run, and invokes /tdd only on yes ⟦criterion 3⟧
- [ ] The README documents /tdd-fix beside /tdd, and the skill ships no scripts ⟦criterion 3⟧
