## skills/veri-bail/SKILL.md

| ID | Requirement | Why |
|---|---|---|
| B1 | Invoked as `/veri-bail <issue>`. `veri-dev` calls it on every exit that is not ✅ Done. | |
| B2 | It classifies from facts before acting: usage limit, sleep, killed-stuck, a budget, revise-exhausted, red baseline, a ledger question. | Not from the comment's wording. |
| B3 | A usage limit or sleep is not a bail: it saves any uncommitted leaf edit as a patch, restores the tree, and resumes when usage is back. | |
| B4 | A first real bail is resumed once, with `VERI_NEW_SKILL=1` when the fix it needs landed after its launch. | |
| B5 | A second bail is parked: one issue comment with the cause and what would unblock it, then the next issue is taken. | |
| B6 | Budget raises and ledger amendments come only from the coordinator or the human, and apply to that one resume. | |
| B7 | It leaves the run's logs in place. | |
