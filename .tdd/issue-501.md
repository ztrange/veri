# Plan for #501 — a skill that turns architecture-analysis candidates into veri-shaped issues

- [ ] A new veri skill ships as its own directory under skills/ whose SKILL.md frontmatter name matches the directory, and it says it shapes and files candidates without surveying, ranking or judging them
- [ ] Given architecture-analysis candidates taken from the conversation, the skill files one GitHub issue per module (not one per smell), each with acceptance criteria phrased as structural predicates carrying a runnable check where one exists ⟦criterion 1⟧
- [ ] Given the path to the analysis's HTML report instead of conversation candidates, the skill reads the candidates from that file and files the same issues it would have filed from the conversation ⟦criterion 2⟧
- [ ] Every issue the skill files ends its body with a final `Test command:` line and lists under `## Blocked by` only real blockers ⟦criterion 3⟧
- [ ] A candidate with no checkable predicate is not filed, and the skill says which candidate was skipped and why ⟦criterion 4⟧
- [ ] Re-running the skill over candidates it already filed files no duplicate issue for them ⟦criterion 5⟧
