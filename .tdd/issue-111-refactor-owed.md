### skills/tdd-fix/SKILL.md exists as the /tdd-fix skill, taking an optional one-line description and asking only for what that line left out, in one short round ⟦criterion 1⟧
- extract `frontmatter_name`, `report` and the frontmatter/body awk shared by `skill-fix-identity.test.sh` and `skill-identity.test.sh` into a sourced test helper — against the repo's self-contained-suite idiom, so it needs a decision first
### The issue body it files carries exactly the six headings the conductor reads — What happened, Expected, Steps to reproduce, Environment, Acceptance criteria, and Blocked by holding None ⟦criterion 1⟧
- fold the shared leading-`---` frontmatter scan of frontmatter_name and body_text into one awk preamble (low value: awk has no clean way to share it, and both helpers get harder to read)
### The skill asks one question before starting the fix run, and invokes /tdd only on yes ⟦criterion 3⟧
- fold case 3's inline empty-criteria guard together with `have_body`'s fail-closed check — both are `[[ -n "${text// /}" ]]` plus a differing sentence, so a shared `have_prose <what>` would end up as thin as its two callers
